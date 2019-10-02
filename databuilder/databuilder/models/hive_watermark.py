from databuilder.models.watermark import Watermark
import warnings
warnings.warn("HiveWatermark class is deprecated. Use Watermark instead",
              DeprecationWarning, stacklevel=2)


class HiveWatermark(Watermark):
    # type: (...) -> None
    """
    Hive table watermark result model.
    Each instance represents one row of hive table watermark result.
    """

    def __init__(self,
                 create_time,  # type: str
                 schema_name,  # type: str
                 table_name,  # type: str
                 part_name,  # type: str
                 part_type='high_watermark',  # type: str
                 cluster='gold',  # type: str
                 ):
        # type: (...) -> None
        super(HiveWatermark, self).__init__(create_time=create_time,
                                            database='hive',
                                            schema_name=schema_name,
                                            table_name=table_name,
                                            part_name=part_name,
                                            part_type=part_type,
                                            cluster=cluster,
                                            )
