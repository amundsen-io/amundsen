# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from typing import (
    Any, Dict, Iterator, Optional,
)

from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.extractor.dashboard.databricks_sql.databricks_sql_dashboard_utils import (
    DatabricksSQLPaginatedRestApiQuery, generate_dashboard_description, get_text_widgets, get_visualization_widgets,
    sort_widgets,
)
from databuilder.extractor.restapi.rest_api_extractor import REST_API_QUERY, RestAPIExtractor
from databuilder.models.dashboard.dashboard_chart import DashboardChart
from databuilder.models.dashboard.dashboard_last_modified import DashboardLastModifiedTimestamp
from databuilder.models.dashboard.dashboard_metadata import DashboardMetadata
from databuilder.models.dashboard.dashboard_owner import DashboardOwner
from databuilder.models.dashboard.dashboard_query import DashboardQuery
from databuilder.rest_api.base_rest_api_query import EmptyRestApiQuerySeed
from databuilder.rest_api.rest_api_query import RestApiQuery
from databuilder.transformer.base_transformer import ChainedTransformer
from databuilder.transformer.timestamp_string_to_epoch import FIELD_NAME as TS_FIELD_NAME, TimestampStringToEpoch


class DatabricksSQLDashboardExtractor(Extractor):
    """
    An extractor for retrieving dashboards, queries, and visualizations
    from Databricks SQL (https://databricks.com/product/databricks-sql)
    """

    DATABRICKS_HOST_KEY = "databricks_host"
    DATABRICKS_API_TOKEN_KEY = "databricks_api_token"

    PRODUCT = "databricks-sql"
    DASHBOARD_GROUP_ID = "databricks-sql"
    DASHBOARD_GROUP_NAME = "Databricks SQL"

    def init(self, conf: ConfigTree) -> None:
        # Required configuration
        self._databricks_host = conf.get_string(
            DatabricksSQLDashboardExtractor.DATABRICKS_HOST_KEY
        )
        self._databricks_api_token = conf.get_string(
            DatabricksSQLDashboardExtractor.DATABRICKS_API_TOKEN_KEY
        )

        # NOTE: The dashboards api is currently in preview. When it gets moved out of preview
        # this will break and it will need to be changed
        self._databricks_sql_dashboards_api_base = (
            f"{self._databricks_host}/api/2.0/preview/sql/dashboards"
        )

        self._extractor = self._build_extractor()
        self._transformer = self._build_transformer()
        self._extract_iter: Optional[Iterator[Any]] = None

    def _get_databrick_request_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._databricks_api_token}",
        }

    def _get_extract_iter(self) -> Iterator[Any]:
        while True:
            record = self._extractor.extract()
            if not record:
                break

            record = next(self._transformer.transform(record=record), None)
            dashboard_identity_data = {
                "dashboard_group_id": DatabricksSQLDashboardExtractor.DASHBOARD_GROUP_ID,
                "dashboard_id": record["dashboard_id"],
                "product": "databricks-sql",
            }

            dashboard_data = {
                "dashboard_group": DatabricksSQLDashboardExtractor.DASHBOARD_GROUP_NAME,
                "dashboard_name": record["dashboard_name"],
                "dashboard_url": f"{self._databricks_host}/sql/dashboards/{record['dashboard_id']}",
                "dashboard_group_url": self._databricks_host,
                "created_timestamp": record["created_timestamp"],
                "tags": record["tags"],
            }

            dashboard_owner_data = {"email": record["user"]["email"]}
            dashboard_owner_data.update(dashboard_identity_data)
            yield DashboardOwner(**dashboard_owner_data)

            dashboard_last_modified_data = {
                "last_modified_timestamp": record["last_modified_timestamp"],
            }
            dashboard_last_modified_data.update(dashboard_identity_data)
            yield DashboardLastModifiedTimestamp(**dashboard_last_modified_data)

            if "widgets" in record:
                widgets = sort_widgets(record["widgets"])
                text_widgets = get_text_widgets(widgets)
                viz_widgets = get_visualization_widgets(widgets)
                dashboard_data["description"] = generate_dashboard_description(
                    text_widgets, viz_widgets
                )

                for viz in viz_widgets:
                    dashboard_query_data = {
                        "query_id": str(viz.query_id),
                        "query_name": viz.query_name,
                        "url": self._databricks_host + viz.query_relative_url,
                        "query_text": viz.raw_query,
                    }
                    dashboard_query_data.update(dashboard_identity_data)
                    yield DashboardQuery(**dashboard_query_data)

                    dashboard_chart_data = {
                        "query_id": str(viz.query_id),
                        "chart_id": str(viz.visualization_id),
                        "chart_name": viz.visualization_name,
                        "chart_type": viz.visualization_type,
                    }
                    dashboard_chart_data.update(dashboard_identity_data)
                    yield DashboardChart(**dashboard_chart_data)

            dashboard_data.update(dashboard_identity_data)
            yield DashboardMetadata(**dashboard_data)

    def extract(self) -> Any:
        if not self._extract_iter:
            self._extract_iter = self._get_extract_iter()
        try:
            return next(self._extract_iter)
        except StopIteration:
            return None

    def _build_extractor(self) -> RestAPIExtractor:
        extractor = RestAPIExtractor()
        rest_api_extractor_conf = ConfigFactory.from_dict(
            {REST_API_QUERY: self._build_restapi_query()}
        )
        extractor.init(rest_api_extractor_conf)
        return extractor

    def _build_transformer(self) -> ChainedTransformer:
        transformers = []
        # transform timestamps from ISO to unix epoch
        ts_transformer_1 = TimestampStringToEpoch()
        ts_transformer_1.init(
            ConfigFactory.from_dict({TS_FIELD_NAME: "created_timestamp"})
        )
        transformers.append(ts_transformer_1)

        ts_transformer_2 = TimestampStringToEpoch()
        ts_transformer_2.init(
            ConfigFactory.from_dict({TS_FIELD_NAME: "last_modified_timestamp"})
        )
        transformers.append(ts_transformer_2)

        return ChainedTransformer(transformers=transformers)

    def _build_restapi_query(self) -> RestApiQuery:
        databricks_sql_dashboard_query = DatabricksSQLPaginatedRestApiQuery(
            query_to_join=EmptyRestApiQuerySeed(),
            url=self._databricks_sql_dashboards_api_base,
            params={"headers": self._get_databrick_request_headers()},
            json_path="results[*].[id,name,tags,updated_at,created_at,user]",
            field_names=[
                "dashboard_id",
                "dashboard_name",
                "tags",
                "last_modified_timestamp",
                "created_timestamp",
                "user",
            ],
            skip_no_results=True,
        )

        return RestApiQuery(
            query_to_join=databricks_sql_dashboard_query,
            url=f"{self._databricks_sql_dashboards_api_base}/{{dashboard_id}}",
            params={"headers": self._get_databrick_request_headers()},
            json_path="widgets",
            field_names=["widgets"],
            skip_no_result=True,
        )

    def get_scope(self) -> str:
        return "extractor.databricks_sql_extractor"
