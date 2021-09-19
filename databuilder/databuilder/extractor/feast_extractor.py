# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Iterator, Union

import yaml
from feast import FeatureStore, FeatureView
from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_metadata import ColumnMetadata, TableMetadata


class FeastExtractor(Extractor):
    """
    Extracts feature tables from Feast Core service. Since Feast is
    a metadata store (and not the database itself), it maps the
    following atributes:

     * a database is name of feast project
     * table name is a name of the feature table
     * columns are features stored in the feature table
    """

    FEAST_REPOSITORY_PATH = "/path/to/repository"
    DESCRIBE_FEATURE_VIEWS = "describe_feature_views"
    DEFAULT_CONFIG = ConfigFactory.from_dict(
        {FEAST_REPOSITORY_PATH: ".", DESCRIBE_FEATURE_VIEWS: True}
    )

    def init(self, conf: ConfigTree) -> None:
        conf = conf.with_fallback(FeastExtractor.DEFAULT_CONFIG)
        self._feast_repository_path = conf.get_string(FeastExtractor.FEAST_REPOSITORY_PATH)
        self._describe_feature_views = conf.get_bool(
            FeastExtractor.DESCRIBE_FEATURE_VIEWS
        )
        self._feast = FeatureStore(
            repo_path=self._feast_repository_path
        )
        self._extract_iter: Union[None, Iterator] = None

    def get_scope(self) -> str:
        return "extractor.feast"

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

    def _get_extract_iter(self) -> Iterator[TableMetadata]:
        for project in self._client.list_projects():
            for feature_table in self._client.list_feature_tables(project=project):
                yield from self._extract_feature_table(project, feature_table)

    def _extract_feature_table(
        self, project: str, feature_view: FeatureView
    ) -> Iterator[TableMetadata]:
        columns = []
        for index, entity_name in enumerate(feature_view.entities):
            entity = self._feast.get_entity(entity_name, project=project)
            columns.append(
                ColumnMetadata(
                    entity.name, entity.description, entity.value_type, index
                )
            )

        for index, feature in enumerate(feature_view.features):
            columns.append(
                ColumnMetadata(
                    feature.name,
                    None,
                    feature.dtype.name,
                    len(feature_view.entities) + index,
                )
            )

        yield TableMetadata(
            "feast",
            project,
            self._feast.config.provider,
            feature_view.name,
            None,
            columns,
        )

        if self._describe_feature_views:
            created_at = datetime.utcfromtimestamp(
                feature_view.created_timestamp.seconds
            )
            description = f"* Created at **{created_at}**\n"

            if feature_view.labels:
                description += "* Labels:\n"
                for key, value in feature_view.labels.items():
                    description += f"    * {key}: **{value}**\n"

            yield TableMetadata(
                "feast",
                project,
                self._feast.config.provider,
                feature_view.name,
                description,
                description_source="feature_table_details",
            )

            yield TableMetadata(
                "feast",
                project,
                self._feast.config.provider,
                feature_view.name,
                f'```\n{yaml.dump(feature_view.to_dict()["spec"]["batchSource"])}```',
                description_source="batch_source",
            )

            if feature_view.stream_source:
                yield TableMetadata(
                    "feast",
                    project,
                    self._feast.config.provider,
                    feature_view.name,
                    f'```\n{yaml.dump(feature_view.to_dict()["spec"]["streamSource"])}```',
                    description_source="stream_source",
                )
