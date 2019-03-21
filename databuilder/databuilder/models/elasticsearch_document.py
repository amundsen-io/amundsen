from abc import ABCMeta, abstractmethod


class ElasticsearchDocument:
    """
    Base class for ElasticsearchDocument
    Each different resource ESDoc will be a subclass
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_json(self):
        # type: () -> str
        """
        Convert object to json for elasticsearch bulk upload
        Bulk load JSON format is defined here:
        https://www.elastic.co/guide/en/elasticsearch/reference/6.2/docs-bulk.html
        :return:
        """
        pass
