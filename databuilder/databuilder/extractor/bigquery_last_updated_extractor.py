from typing import Iterator
from google.cloud import bigquery
from pyhocon import ConfigTree

from databuilder.models.table_last_updated import TableLastUpdated
from databuilder.extractor.base_bigquery_extractor import BaseBigQueryExtractor

class BigQueryLastUpdatedExtractor(BaseBigQueryExtractor):
    
    """ A last updated extractor for bigquery tables, taking a project_id and an specific
    dataset location from google cloud bigquery API's. This extractor goes through all visible
    datasets in the project in an specific region identifing the last updated recrod. 
    """

    DATASET_LOCATION = "EU"

    def init(self, conf: ConfigTree) -> None:
        BaseBigQueryExtractor.init(self, conf)
        self.bigquery_client = bigquery.Client.from_service_account_json(self.key_path)
        self.dataset_location = conf.get_string(BigQueryLastUpdatedExtractor.DATASET_LOCATION)
        self.iter: Iterator[TableLastUpdated] = iter(self._extract_last_updated_timestamp())

    def _get_datasets_metadata(self):

        return list(self._page_dataset_list_results())[0]["datasets"]

    def _generate_query(self):

        datasets_metadata = self._get_datasets_metadata()
        datasets_ids = [
            dataset["id"].split(":")[-1]
            for dataset in datasets_metadata
            if dataset["location"] == self.dataset_location
        ]

        datasets_query_list = [
            f"""SELECT 
                                   dataset_id,
                                   table_id,
                                   TIMESTAMP_TRUNC(TIMESTAMP_MILLIS(last_modified_time), MINUTE) AS table_last_modified_timestamp,
                                   row_count
                                   FROM {dataset_id}.__TABLES__ table_updates"""
            for dataset_id in datasets_ids
        ]

        return " UNION ALL ".join(datasets_query_list)

    def _extract_last_updated_timestamp(self) -> Iterator[TableLastUpdated]:

        try:
            dataset_query = self._generate_query()
            query_results = self.bigquery_client.query(dataset_query)
            records = list(query_results.result())
            for record in records:
                yield TableLastUpdated(
                    schema=record[0],
                    table_name=record[1],
                    last_updated_time_epoch=record[2].timestamp(),
                    db="bigquery",
                    cluster=self.project_id,
                )
        except StopIteration:
            return None

    def get_scope(self) -> str:
        return "extractor.bigquery_last_updated"
