# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
import json
import logging
import os
from typing import Dict, Iterator, Union

from pyhocon import ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.badge import Badge, BadgeMetadata
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata
from databuilder.models.table_lineage import TableLineage
from databuilder.models.table_source import TableSource


LOGGER = logging.getLogger(__name__)


DBT_CATALOG_REQD_KEYS = ['nodes']
DBT_MANIFEST_REQD_KEYS = ['nodes', 'child_map']
DBT_MODEL_PREFIX = 'model.'
DBT_TEST_PREFIX = 'test.'


class DBT_TAG_AS(Enum):
    BADGE = 'badge'
    TAG = 'tag'


class InvalidDbtInputs(Exception):
    pass


class DbtExtractor(Extractor):
    """
    Extracts metadata from the dbt manifest.json and catalog.json files.
    At least one of a manifest or a catalog (or both) must be provided.
    The location of the file or a valid Python dictionary of the content
    can be provided.

    Currently the following assets are extracted from these files:

    - Tables
    - Columns
    - Definitions
    - Table lineage
    - Tags (converted to Amundsen Badges)

    Additional metadagta exists and may be extracted in the future:

    - Run / test outcomes
    - Freshness
    - Hooks (as programatic description?)
    - Analysis (as queries for a table??)
    - Table / column level statistics
    - Table comments (as programatic descriptoins)
    """

    CATALOG_JSON = "catalog_json"
    MANIFEST_JSON = "manifest_json"
    DATABASE_NAME = 'database_name'

    # Dbt Extract Options
    EXTRACT_TABLES = 'extract_tables'
    EXTRACT_DESCRIPTIONS = 'extract_descriptions'
    EXTRACT_TAGS = 'extract_tags'
    EXTRACT_LINEAGE = 'extract_lineage'
    SOURCE_URL = 'source_url'  # Base source code URL for the repo containing dbt workflows
    IMPORT_TAGS_AS = 'import_tags_as'

    # Makes all db, schema, cluster and table names lowercase. This is done so that table metadata from dbt
    # with the default key `Sample://Cluster/Schema/Table` match existing metadata that Amundsen has from
    # the database, which may be `sample://cluster/schema/table`.
    # Most databases that dbt integrates with either use lowercase by default in the information schema
    # or the default Amundsen extractor applies a `lower(...)` function to the result (e.g. snowflake).
    # However, Amundsen does not currently enforce a consistent convention and some databases do support
    # upper and lowercase naming conventions (e.g. Redshift). It may be useful to set this False in the
    # config if the table metadata keys in your database are not all lowercase and to then use a transformer to
    # properly format the string value.
    FORCE_TABLE_KEY_LOWER = 'force_table_key_lower'

    def init(self, conf: ConfigTree) -> None:
        self._conf = conf
        self._database_name = conf.get_string(DbtExtractor.DATABASE_NAME)
        self._dbt_manifest = conf.get_string(DbtExtractor.MANIFEST_JSON)
        self._dbt_catalog = conf.get_string(DbtExtractor.CATALOG_JSON)
        # Extract options
        self._extract_tables = conf.get_bool(DbtExtractor.EXTRACT_TABLES, True)
        self._extract_descriptions = conf.get_bool(DbtExtractor.EXTRACT_DESCRIPTIONS, True)
        self._extract_tags = conf.get_bool(DbtExtractor.EXTRACT_TAGS, True)
        self._extract_lineage = conf.get_bool(DbtExtractor.EXTRACT_LINEAGE, True)
        self._source_url = conf.get_string(DbtExtractor.SOURCE_URL, None)
        self._force_table_key_lower = conf.get_bool(DbtExtractor.FORCE_TABLE_KEY_LOWER, True)
        self._dbt_tag_as = DBT_TAG_AS(conf.get_string(DbtExtractor.IMPORT_TAGS_AS, DBT_TAG_AS.BADGE.value))
        self._clean_inputs()

        self._extract_iter: Union[None, Iterator] = None

    def get_scope(self) -> str:
        return "extractor.dbt"

    def _validate_catalog(self) -> None:
        # Load the catalog file if needed and run basic validation on the content
        try:
            self._dbt_catalog = json.loads(self._dbt_catalog)
        except Exception:
            try:
                with open(self._dbt_catalog, 'rb') as f:
                        self._dbt_catalog = json.load(f)
            except Exception as e:
                raise InvalidDbtInputs(
                    'Invalid content for a dbt catalog was provided. Must be a valid Python '
                    'dictionary or the location of a file. Error received: %s' % e
                )
        for catalog_key in DBT_CATALOG_REQD_KEYS:
            if catalog_key not in self._dbt_catalog:
                raise InvalidDbtInputs(
                    "Dbt catalog file must contain keys: %s, found keys: %s"
                    % (DBT_CATALOG_REQD_KEYS, self._dbt_catalog.keys())
                )

    def _validate_manifest(self) -> None:
        # Load the manifest file if needed and run basic validation on the content
        try:
            self._dbt_manifest = json.loads(self._dbt_manifest)
        except Exception:
            try:
                with open(self._dbt_manifest, 'rb') as f:
                    self._dbt_manifest = json.load(f)
            except Exception as e:
                raise InvalidDbtInputs(
                    'Invalid content for a dbt manifest was provided. Must be a valid Python '
                    'dictionary or the location of a file. Error received: %s' % e
                )
        for manifest_key in DBT_MANIFEST_REQD_KEYS:
            if manifest_key not in self._dbt_manifest:
                raise InvalidDbtInputs(
                    "Dbt manifest file must contain keys: %s, found keys: %s"
                    % (DBT_MANIFEST_REQD_KEYS, self._dbt_manifest.keys())
                )

    def _clean_inputs(self) -> None:
        """
        Validates the dbt input to ensure that at least one of the inputs
        (manifest.json or catalog.json) are provided. Once validated, the
        inputs are sanitized to ensure that the `self._dbt_manifest` and
        `self._dbt_catalog` are valid Python dictionaries.
        """
        if self._database_name is None:
            raise InvalidDbtInputs(
                'Must provide a database name that corresponds to this dbt catalog and manifest.'
            )

        if not self._dbt_manifest or not self._dbt_catalog:
            raise InvalidDbtInputs(
                'Must provide a dbt manifest file and dbt catalog file.'
            )

        self._validate_catalog()
        self._validate_manifest()

    def extract(self) -> Union[TableMetadata, None]:
        """
        For every feature table from Feast, a multiple objets are extracted:

        1. TableMetadata with feature table description
        2. Programmatic Description of the feature table, containing
           metadata - date of creation and labels
        3. Programmatic Description with Batch Source specification
        4. (if applicable) Programmatic Description with Stream Source
           specification
        """
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def _get_col_full_name(self, tbl_node: str, col_name: str) -> str:
        """
        Generates a string that represents the table/column relationship. This is only used
        within this class to correlate metadata between the catalog.json and the manifest.json.
        """
        return f'{tbl_node}.{col_name}'.lower()

    def _default_sanitize(self, s: str) -> str:
        """
        Default function that will be run to convert the value of a string to lowercase.
        """
        if s and self._force_table_key_lower:
            s = s.lower()
        return s

    def _remove_empty_keys(self, d: Dict) -> Dict:
        """
        Removes all keys in a dictionary where the value is empty or null
        """
        return {k: v for k, v in d.items() if v}

    def _get_extract_iter(self) -> Iterator[Union[TableMetadata, BadgeMetadata, TableSource, TableLineage]]:

        tables = self._extract_catalog_content()
        self._update_from_manifest(tables)

        # Keep track of table to metadata to generate lineage at the end
        dbt_id_to_table_key = {}
        for table_id, table in tables.items():
            table_cols = table['columns']
            col_metadata = [ColumnMetadata(**col) for col in table_cols.values()]

            table['columns'] = col_metadata
            tbl_badges = table.pop('_badges', None)
            tbl_source = table.pop('_source_url', None)
            tbl_metedata = TableMetadata(**table)
            dbt_id_to_table_key[table_id] = tbl_metedata._get_table_key()

            if self._extract_tables:
                yield tbl_metedata

            if self._extract_tags and tbl_badges:
                yield BadgeMetadata(start_label=TableMetadata.TABLE_NODE_LABEL,
                                    start_key=tbl_metedata._get_table_key(),
                                    badges=[Badge(badge, 'table') for badge in tbl_badges])

            if self._source_url and tbl_source:
                yield TableSource(db_name=tbl_metedata.database,
                                  cluster=tbl_metedata.cluster,
                                  schema=tbl_metedata.schema,
                                  table_name=tbl_metedata.name,
                                  source=os.path.join(self._source_url, tbl_source))

        if self._extract_lineage:
            for upstream, downstreams in self._dbt_manifest['child_map'].items():
                valid_downstreams = [
                    dbt_id_to_table_key[k] for k in downstreams if k.startswith(DBT_MODEL_PREFIX)
                ]
                if valid_downstreams:
                    yield TableLineage(
                        table_key=dbt_id_to_table_key[upstream],
                        downstream_deps=valid_downstreams
                    )

    def _get_columns_from_catalog(self, tbl_node: str, table_columns: Dict) -> Dict:
        """
        The catalog file has metadata about all columns for the tables / views
        that are created by dbt even if those tables, views and columns are not
        defined in a corresponding schema.yml file. The input for this function
        looks like:
        {
            "DT": {
                "type": "NUMBER",
                "index": 1,
                "name": "DT",
                "comment": null
            },
            "INVENTORY_COST": {
                "type": "NUMBER",
                "index": 2,
                "name": "INVENTORY_COST",
                "comment": null
            }
        }

        :params tbl_node: the dbt node ID for the table, used to generate a unique
            column ID
        :params table_columns: A dictionary where the keys are the name of the column
            and the values are the metedata for the
        :returns: a dictionary of values that can be used to build a single
            `ColumnMetadata` in Amundsen.
        """
        tbl_columns = {}
        for col_name, col_content in table_columns.items():
            tbl_col_name = self._get_col_full_name(tbl_node, col_name)
            tbl_columns[tbl_col_name] = dict(
                name=self._default_sanitize(col_content['name']),
                description=None,
                col_type=col_content['type'],
                sort_order=col_content['index'],
                badges=None,
                # TODO: use this in the future if columns have programatic descriptions?
                # col_comment = col_content['comment']
            )
        return tbl_columns

    def _extract_catalog_content(self) -> Dict:
        """
        Extracts metadata from the catalog file content. It is expected that
        some of this information will be updated by the manifest file after it
        is processed as well.
        """
        tables: Dict = {}

        for tbl_node, tbl_content in self._dbt_catalog['nodes'].items():

            # Extract column metadata for the table
            tbl_columns = self._get_columns_from_catalog(tbl_node=tbl_node, table_columns=tbl_content['columns'])

            # TODO Add this as a table-level programatic desc
            # Cannot get dbt to fill in this value for some reason..
            # tbl_comment = tbl_content['metadata']['comment']

            # TODO get column stats here
            # for col_name, col_stat in tbl_content['stats'].items():
            #     ...

            # Since table/column metadata objects call `_create_next_node`, `_create_next_relation`,
            # etc. on init and half of the metadata we need could potentially be in the other file we need
            # to keep track of this information and create the metadata objects after combining the data
            table = dict(
                database=self._default_sanitize(self._database_name),
                # The dbt "database" is the cluster here
                cluster=self._default_sanitize(tbl_content['metadata']['database']),
                schema=self._default_sanitize(tbl_content['metadata']['schema']),
                name=self._default_sanitize(tbl_content['metadata']['name']),
                description=None,
                columns=tbl_columns,
                is_view=tbl_content['metadata']['type'] == 'VIEW',
                tags=None,
                description_source=None,
            )
            tables[tbl_node] = table

        return tables

    def _update_columns_from_manifest(self, existing_metadata: Dict,
                                      tbl_node: str, manifest_tbl_columns: Dict) -> None:
        """
        Column level information is only available in the manifest file if explicitly defined
        in a schema.yml. This function updates the existing column level metadata from
        the catalog.json if it exists.

        :params existing_metadata: a dictionary of all existing metadata from the catalog.json. Generally
            looks like
                >>> {
                >>>    "table_id": {
                >>>        "col1": {...},
                >>>        "col2": {...}
                >>>        ...
                >>>    }
                >>> }
        :params tbl_node: The unique ID used to represent the table.
        :returns: None, all values in the dictionary are updated directly
        """
        for col_name, col_content in manifest_tbl_columns.items():
            tbl_col_name = self._get_col_full_name(tbl_node, col_name)
            tbl_col_update: Dict = {}

            # TODO: What to do with column meta? Could be useful for column-level prog desc
            # col_meta = col_content['meta]

            if self._extract_descriptions:
                tbl_col_update['description'] = col_content.get('description')

            # Only extract column-level tags IF converting to badges, Amundsen does not have column-level tags
            if self._extract_tags and self._dbt_tag_as == DBT_TAG_AS.BADGE:
                tbl_col_update['badges'] = col_content.get('tags')

            # Update the columns
            existing_metadata[tbl_node]['columns'][tbl_col_name].update(self._remove_empty_keys(tbl_col_update))

    def _update_from_manifest(self, tables: Dict) -> None:
        """
        Extracts metadata from the manifest file, updating the information
        previously extracted from the catalog file where applicable.
        :param tables: A dictionary containing keys that can generate a table metadata
            object
        :returns: None, by updating the dictionary directly it does not need to be returned
        """

        # Process the manifest file. This has overlapping and orthogonal metadata
        manifest_nodes = self._dbt_manifest['nodes']
        for tbl_node, tbl_content in manifest_nodes.items():

            # TODO - handle dbt tests / data quality
            # if tbl_node.startswith(DBT_TEST_PREFIX):
            #     ...

            # Process dbt models
            if tbl_node.startswith(DBT_MODEL_PREFIX):

                self._update_columns_from_manifest(
                    existing_metadata=tables,
                    tbl_node=tbl_node,
                    manifest_tbl_columns=tbl_content['columns']
                )

                # Update the incremental table metadata captured from the manifest file
                manifest_table: Dict = {}

                if self._extract_descriptions:
                    desc = tbl_content.get('description')
                    if desc:
                        manifest_table['description'] = desc
                        manifest_table['description_source'] = 'dbt description'

                if self._extract_tags:
                    if self._dbt_tag_as == DBT_TAG_AS.BADGE:
                        manifest_table['_badges'] = tbl_content.get('tags')
                    elif self._dbt_tag_as == DBT_TAG_AS.TAG:
                        manifest_table['tags'] = tbl_content.get('tags')

                if self._source_url:
                    manifest_table['_source_url'] = tbl_content.get('original_file_path')

                # TODO - associate SQL to table
                # compiled_sql = tbl_content['compiled_sql']

                # Update the table
                tables[tbl_node].update(self._remove_empty_keys(manifest_table))
