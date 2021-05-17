import json
from typing import (
    Any, Dict, Tuple,
)

import dateutil.parser
from pyhocon import ConfigFactory, ConfigTree

from databuilder.extractor.base_extractor import Extractor
from databuilder.models.table_stats import TableColumnStats


class PandasProfilingColumnStatsExtractor(Extractor):
    FILE_PATH = 'file_path'
    DATABASE_NAME = 'database_name'
    TABLE_NAME = 'table_name'
    SCHEMA_NAME = 'schema_name'
    CLUSTER_NAME = 'cluster_name'

    # if you wish to collect only selected set of metrics configure stat_mappings option of the extractor providing
    # similar dictionary but containing only keys of metrics you wish to collect.
    # For example - if you want only min and max value of a column, provide extractor with configuration option:
    # PandasProfilingColumnStatsExtractor.STAT_MAPPINGS = {'max': ('Maximum', float), 'min': ('Minimum', float)}
    STAT_MAPPINGS = 'stat_mappings'

    # - key - raw name of the stat in pandas-profiling. Value - tuple of stat spec.
    # - first value of the tuple - full name of the stat
    # - second value of the tuple - function modifying the stat (by default we just do type casting)
    DEFAULT_STAT_MAPPINGS = {
        '25%': ('Quantile 25%', float),
        '5%': ('Quantile 5%', float),
        '50%': ('Quantile 50%', float),
        '75%': ('Quantile 75%', float),
        '95%': ('Quantile 95%', float),
        'chi_squared': ('Chi squared', lambda x: float(x.get('statistic'))),
        'count': ('Count', int),
        'is_unique': ('Is unique', bool),
        'kurtosis': ('Kurtosis', float),
        'max': ('Maximum', float),
        'max_length': ('Maximum length', int),
        'mean': ('Mean', float),
        'mean_length': ('Mean length', int),
        'median_length': ('Median length', int),
        'min': ('Minimum', float),
        'min_length': ('Minimum length', int),
        'monotonic': ('Is monotonic', bool),
        'n_category': ('Categories', int),
        'n_characters': ('Characters', int),
        'n_characters_distinct': ('Distinct characters', int),
        'n_distinct': ('Distinct values', int),
        'n_infinite': ('Infinite values', int),
        'n_missing': ('Missing values', int),
        'n_negative': ('Negative values', int),
        'n_unique': ('Unique values', int),
        'n_zeros': ('Zeros', int),
        'p_distinct': ('Distinct values %', lambda x: f'{round(100 * x, 2)}%'),
        'p_infinite': ('Infinite values %', lambda x: f'{round(100 * x, 2)}%'),
        'p_missing': ('Missing values %', lambda x: f'{round(100 * x, 2)}%'),
        'p_negative': ('Negative values %', lambda x: f'{round(100 * x, 2)}%'),
        'p_unique': ('Unique values %', lambda x: f'{round(100 * x, 2)}%'),
        'p_zeros': ('Zeros %', lambda x: f'{round(100 * x, 2)}%'),
        'range': ('Range', int),
        'skewness': ('Skewness', float),
        'std': ('Standard deviation', float),
        'sum': ('Sum', float),
        'type': ('Type', str),
        'variance': ('Variance', int)
        # Stats available in pandas-profiling but are not collected by default and require custom, conscious config..
        # 'block_alias_char_counts': ('',),
        # 'block_alias_counts': ('',),
        # 'block_alias_values': ('',),
        # 'category_alias_char_counts': ('',),
        # 'category_alias_counts': ('',),
        # 'category_alias_values': ('',),
        # 'character_counts': ('',),
        # 'cv': ('',),
        # 'first_rows': ('',),
        # 'hashable': ('',),
        # 'histogram': ('',),
        # 'histogram_frequencies': ('',),
        # 'histogram_length': ('',),
        # 'iqr': ('',),
        # 'length': ('',),
        # 'mad': ('',),
        # 'memory_size': ('',),
        # 'monotonic_decrease': ('Monotonic decrease', bool),
        # 'monotonic_decrease_strict': ('Strict monotonic decrease', bool),
        # 'monotonic_increase': ('Monotonic increase', bool),
        # 'monotonic_increase_strict': ('Strict monotonic increase', bool),
        # 'n': ('',),
        # 'n_block_alias': ('',),
        # 'n_scripts': ('',),
        # 'ordering': ('',),
        # 'script_char_counts': ('',),
        # 'script_counts': ('',),
        # 'value_counts_index_sorted': ('',),
        # 'value_counts_without_nan': ('',),
        # 'word_counts': ('',)
    }

    DEFAULT_CONFIG = ConfigFactory.from_dict({STAT_MAPPINGS: DEFAULT_STAT_MAPPINGS})

    def get_scope(self) -> str:
        return 'extractor.pandas_profiling'

    def init(self, conf: ConfigTree) -> None:
        self.conf = conf.with_fallback(PandasProfilingColumnStatsExtractor.DEFAULT_CONFIG)

        self._extract_iter = self._get_extract_iter()

    def extract(self) -> Any:
        try:
            result = next(self._extract_iter)

            return result
        except StopIteration:
            return None

    def _get_extract_iter(self) -> Any:
        report = self._load_report()

        variables = report.get('variables', dict())
        report_time = self._get_report_time(report)

        for column_name, column_stats in variables.items():
            for _stat_name, stat_value in column_stats.items():
                stat_spec = self.stat_mappings.get(_stat_name)

                if stat_spec:
                    stat_name, stat_modifier = stat_spec
                    stat_name = stat_name.lower().replace(' ', '_')

                    stat = TableColumnStats(table_name=self.table_name, col_name=column_name, stat_name=stat_name,
                                            stat_val=stat_modifier(stat_value), start_epoch=report_time, end_epoch='0',
                                            db=self.database_name, cluster=self.cluster_name, schema=self.schema_name)

                    yield stat

    def _load_report(self) -> Dict[str, Any]:
        path = self.conf.get(PandasProfilingColumnStatsExtractor.FILE_PATH)

        try:
            with open(path, 'r') as f:
                _data = f.read()

            data = json.loads(_data)

            return data
        except Exception:
            return {}

    @staticmethod
    def _get_report_time(report: Dict[str, Any]) -> str:
        _date = report.get('analysis', dict()).get('date_start')
        result = '0'

        if _date:
            _date = f'{_date}+0000'

            try:
                result = str(int(dateutil.parser.parse(_date).timestamp()))
            except Exception:
                pass

        return result

    @property
    def stat_mappings(self) -> Dict[str, Tuple[str, Any]]:
        return dict(self.conf.get(PandasProfilingColumnStatsExtractor.STAT_MAPPINGS))

    @property
    def cluster_name(self) -> str:
        return self.conf.get(PandasProfilingColumnStatsExtractor.CLUSTER_NAME)

    @property
    def database_name(self) -> str:
        return self.conf.get(PandasProfilingColumnStatsExtractor.DATABASE_NAME)

    @property
    def schema_name(self) -> str:
        return self.conf.get(PandasProfilingColumnStatsExtractor.SCHEMA_NAME)

    @property
    def table_name(self) -> str:
        return self.conf.get(PandasProfilingColumnStatsExtractor.TABLE_NAME)
