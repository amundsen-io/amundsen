import abc
from functools import reduce
from typing import (
    Any, Dict, Generator, Iterator, List, Tuple,
)

import requests
from bs4 import BeautifulSoup
from dateutil import parser
from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor

type_fields_mapping = List[Tuple[str, str, Any, Any]]


class ApacheSupersetBaseExtractor(Extractor):
    """
    Base class to create extractors pulling any dashboard metadata from Apache Superset.
    """
    APACHE_SUPERSET_PROTOCOL = 'apache_superset_protocol'
    APACHE_SUPERSET_HOST = 'apache_superset_host'
    APACHE_SUPERSET_PORT = 'apache_superset_port'
    APACHE_SUPERSET_USER = 'apache_superset_user'
    APACHE_SUPERSET_PASSWORD = 'apache_superset_password'
    APACHE_SUPERSET_PAGE_SIZE = 'apache_superset_page_size'
    APACHE_SUPERSET_EXTRACT_PUBLISHED_ONLY = 'apache_superset_extract_published_only'

    DASHBOARD_GROUP_NAME = 'dashboard_group_name'
    DASHBOARD_GROUP_ID = 'dashboard_group_id'
    DASHBOARD_GROUP_DESCRIPTION = 'dashboard_group_description'

    PRODUCT = 'product'
    CLUSTER = 'cluster'

    DRIVER_TO_DATABASE_MAPPING = 'driver_to_database_mapping'

    DEFAULT_DRIVER_TO_DATABASE_MAPPING = {
        'postgresql': 'postgres',
        'mysql+pymysql': 'mysql'
    }

    DATABASE_TO_CLUSTER_MAPPING = 'database_to_cluster_mapping'  # map superset dbs to preferred clusters

    DEFAULT_CONFIG = ConfigFactory.from_dict({
        APACHE_SUPERSET_PROTOCOL: 'http',
        APACHE_SUPERSET_HOST: 'localhost',
        APACHE_SUPERSET_PORT: '8088',
        APACHE_SUPERSET_USER: 'admin',
        APACHE_SUPERSET_PASSWORD: 'admin',
        APACHE_SUPERSET_PAGE_SIZE: 20,
        APACHE_SUPERSET_EXTRACT_PUBLISHED_ONLY: False,
        PRODUCT: 'apache_superset',
        DASHBOARD_GROUP_DESCRIPTION: '',
        DRIVER_TO_DATABASE_MAPPING: DEFAULT_DRIVER_TO_DATABASE_MAPPING,
        DATABASE_TO_CLUSTER_MAPPING: {}
    })

    def init(self, conf: ConfigTree) -> None:
        self.session = requests.Session()
        self.conf = conf.with_fallback(ApacheSupersetBaseExtractor.DEFAULT_CONFIG)
        self._extract_iter = self._get_extract_iter()

        self.authenticate()

    def get_scope(self) -> str:
        return 'extractor.apache_superset'

    def extract(self) -> Any:
        try:
            result = next(self._extract_iter)

            return result
        except StopIteration:
            return None

    def authenticate(self) -> None:
        # first request is to get csrf_token
        login_form = self.session.get(self.build_full_url('login'))

        # get Cross-Site Request Forgery protection token
        soup = BeautifulSoup(login_form.text, 'html.parser')
        csrf_token = soup.find('input', {'id': 'csrf_token'})['value']

        # second request is to set session cookies with csrf token and user credentials
        self.session.post(self.build_full_url('login'),
                          data=dict(username=self.conf.get(ApacheSupersetBaseExtractor.APACHE_SUPERSET_USER),
                                    password=self.conf.get(ApacheSupersetBaseExtractor.APACHE_SUPERSET_PASSWORD),
                                    csrf_token=csrf_token))

    def build_full_url(self, endpoint: str) -> str:
        return f'{self.base_url}/{endpoint}'

    def execute_query(self, url: str, params: dict = {}) -> Dict:
        try:
            return self.session.get(url, params=params).json()
        except Exception:
            return {}

    def execute_paginated_query(self, url: str) -> Generator:
        page = 0

        while True:
            data = self.execute_query(url, params=dict(page=page, page_size=self.page_size))

            if data:
                page += 1

                yield data
            else:
                break

    @property
    def base_url(self) -> str:
        _protocol = self.conf.get(ApacheSupersetBaseExtractor.APACHE_SUPERSET_PROTOCOL)
        _host = self.conf.get(ApacheSupersetBaseExtractor.APACHE_SUPERSET_HOST)
        _port = self.conf.get(ApacheSupersetBaseExtractor.APACHE_SUPERSET_PORT)

        return f'{_protocol}://{_host}:{_port}'

    @property
    def page_size(self) -> int:
        return self.conf.get_int(ApacheSupersetBaseExtractor.APACHE_SUPERSET_PAGE_SIZE)

    @property
    def product(self) -> str:
        return self.conf.get(ApacheSupersetBaseExtractor.PRODUCT)

    @property
    def cluster(self) -> str:
        return self.conf.get(ApacheSupersetBaseExtractor.CLUSTER)

    @property
    def extract_published_only(self) -> bool:
        return self.conf.get(ApacheSupersetBaseExtractor.APACHE_SUPERSET_EXTRACT_PUBLISHED_ONLY)

    @property
    def common_params(self) -> Dict[str, str]:
        return dict(dashboard_group=self.conf.get(ApacheSupersetBaseExtractor.DASHBOARD_GROUP_NAME),
                    dashboard_group_id=self.conf.get(ApacheSupersetBaseExtractor.DASHBOARD_GROUP_ID),
                    dashboard_group_url=self.base_url,
                    dashboard_group_description=self.conf.get(ApacheSupersetBaseExtractor.DASHBOARD_GROUP_DESCRIPTION),
                    product=self.product,
                    cluster=self.cluster)

    @staticmethod
    def parse_date(string_date: str) -> int:
        try:
            return int(parser.parse(string_date).timestamp())
        except Exception:
            return 0

    @staticmethod
    def get_nested_field(input_dict: Dict, field: str) -> Any:
        return reduce(lambda x, y: x.get(y, dict()), field.split('.'), input_dict)

    @staticmethod
    def map_fields(data: Dict, mappings: type_fields_mapping) -> Dict:
        result = dict()

        for mapping in mappings:
            target_field, source_field, transform, default_value = mapping
            value = ApacheSupersetBaseExtractor.get_nested_field(data, source_field)

            if transform:
                value = transform(value)

            result[target_field] = value or default_value

        return result

    @abc.abstractmethod
    def _get_extract_iter(self) -> Iterator[Any]:
        pass
