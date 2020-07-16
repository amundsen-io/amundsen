# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from databuilder.rest_api.rest_api_query import RestApiQuery


def sort_widgets(widgets):
    # type: (Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]
    """
    Sort raw widget data (as returned from the API) according to the position
    of the widgets in the dashboard (top to bottom, left to right)
    Redash does not return widgets in order of their position,
    so we do this to ensure that we look at widgets in a sensible order.
    """

    def row_and_col(widget):
        # these entities usually but not always have explicit rows and cols
        pos = widget['options'].get('position', {})
        return (pos.get('row', 0), pos.get('col', 0))

    return sorted(widgets, key=row_and_col)


def get_text_widgets(widgets):
    # type: (Iterator[Dict[str, Any]]) -> List[RedashTextWidget]
    """
    From the raw set of widget data returned from the API, filter down
    to text widgets and return them as a list of `RedashTextWidget`
    """

    return [RedashTextWidget(widget) for widget in widgets
            if 'text' in widget and 'visualization' not in widget]


def get_visualization_widgets(widgets):
    # type: (Iterator[Dict[str, Any]]) -> List[RedashVisualizationWidget]
    """
    From the raw set of widget data returned from the API, filter down
    to visualization widgets and return them as a list of `RedashVisualizationWidget`
    """

    return [RedashVisualizationWidget(widget) for widget in widgets
            if 'visualization' in widget]


def get_auth_headers(api_key):
    # type: (str) -> Dict[str, str]
    return {'Authorization': 'Key {}'.format(api_key)}


def generate_dashboard_description(text_widgets, viz_widgets):
    # type: (Iterator[RedashTextWidget], Iterator[RedashVisualizationWidget]) -> str
    """
    Redash doesn't have dashboard descriptions, so we'll make our own.
    If there exist any text widgets, concatenate them,
    and use this text as the description for this dashboard.
    If not, put together a list of query names.
    If all else fails, this looks like an empty dashboard.
    """

    if len(text_widgets) > 0:
        return '\n\n'.join([w.text for w in text_widgets])
    elif len(viz_widgets) > 0:
        query_list = '\n'.join(['- {}'.format(v.query_name) for v in set(viz_widgets)])
        return 'A dashboard containing the following queries:\n\n' + query_list

    return 'This dashboard appears to be empty!'


class RedashVisualizationWidget:
    """
    A visualization widget in a Redash dashboard.
    These are mapped 1:1 with queries, and can be of various types, e.g.:
    CHART, TABLE, PIVOT, etc.
    The query name acts like a title for the widget on the dashboard.
    """

    def __init__(self, data):
        # type: (Dict[str, Any]) -> None
        self._data = data

    @property
    def raw_query(self):
        # type () -> str
        return self._data['visualization']['query']['query']

    @property
    def data_source_id(self):
        # type: () -> int
        return self._data['visualization']['query']['data_source_id']

    @property
    def query_id(self):
        # type: () -> int
        return self._data['visualization']['query']['id']

    @property
    def query_relative_url(self):
        # type: () -> str
        return '/queries/{id}'.format(id=self.query_id)

    @property
    def query_name(self):
        # type: () -> str
        return self._data['visualization']['query']['name']


class RedashTextWidget:
    """
    A textbox in a Redash dashboad.
    It pretty much just contains a single text property (Markdown).
    """

    def __init__(self, data):
        # type: (Dict[str, Any]) -> None
        self._data = data

    @property
    def text(self):
        # type: () -> str
        return self._data['text']


class RedashPaginatedRestApiQuery(RestApiQuery):
    """
    Paginated Redash API queries
    """

    def __init__(self, **kwargs):
        # type: (...) -> None
        super(RedashPaginatedRestApiQuery, self).__init__(**kwargs)
        if 'params' not in self._params:
            self._params['params'] = {}
        self._params['params']['page'] = 1

    def _total_records(self, res):
        # type: (Dict[str, Any]) -> int
        return res['count']

    def _max_record_on_page(self, res):
        # type: (Dict[str, Any]) -> int
        return res['page_size'] * res['page']

    def _next_page(self, res):
        # type: (Dict[str, Any]) -> int
        return res['page'] + 1

    def _post_process(self, response):
        # type: (Any) -> None
        parsed = response.json()

        if self._max_record_on_page(parsed) >= self._total_records(parsed):
            self._more_pages = False
        else:
            self._params['params']['page'] = self._next_page(parsed)
            self._more_pages = True
