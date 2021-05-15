from typing import (
    Any, Dict, Iterator, List, Tuple, Union,
)

from databuilder.extractor.dashboard.apache_superset import ApacheSupersetBaseExtractor
from databuilder.models.dashboard.dashboard_chart import DashboardChart
from databuilder.models.dashboard.dashboard_query import DashboardQuery


class ApacheSupersetChartExtractor(ApacheSupersetBaseExtractor):
    def _get_extract_iter(self) -> Iterator[Union[DashboardQuery, DashboardChart, None]]:
        ids = self._get_dashboard_ids()

        data = [self._get_dashboard_details(i) for i in ids]

        for entry in data:
            dashboard_id, dashboard_data, datasource_data = entry

            # Since Apache Superset doesn't support dashboard <> query <> chart relation we create a dummy 'bridge'
            # query node so we can connect charts to a dashboard
            dashboard_query_data = dict(dashboard_id=dashboard_id,
                                        query_name='default',
                                        query_id='-1',
                                        url='',
                                        query_text='')

            dashboard_query_data.update(**self.common_params)

            yield DashboardQuery(**dashboard_query_data)

            charts = [s.get('__Slice__') for s in dashboard_data.get('slices', [])]

            for chart in charts:
                if chart:
                    dashboard_chart_data = dict(
                        dashboard_id=dashboard_id,
                        query_id='-1',
                        chart_id=chart.get('id'),
                        chart_name=chart.get('slice_name'),
                        chart_type=chart.get('viz_type', '').lower(),
                        chart_url=''
                    )

                    dashboard_chart_data.update(self.common_params)

                    yield DashboardChart(**dashboard_chart_data)

    def _get_dashboard_ids(self) -> List[str]:
        url = self.build_full_url(f'api/v1/dashboard')

        data = self.execute_query(url)

        return data.get('ids', [])

    def _get_dashboard_details(self, dashboard_id: str) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        url = self.build_full_url(f'api/v1/dashboard/export?q=[{dashboard_id}]')

        dashboard_data = self.execute_query(url).get('dashboards', [])[0].get('__Dashboard__', dict())
        datasources_data = self.execute_query(url).get('datasources', [])

        data = dashboard_id, dashboard_data, datasources_data

        return data
