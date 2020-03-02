import textwrap

# Specifying default mapping for elasticsearch index
# Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
# Setting type to "text" for all fields that would be used in search
# Using Simple Analyzer to convert all text into search terms
# https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-simple-analyzer.html
# Standard Analyzer is used for all text fields that don't explicitly specify an analyzer
# https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-standard-analyzer.html
DEFAULT_ELASTICSEARCH_INDEX_MAPPING = textwrap.dedent(
    """
    {
    "mappings":{
        "table":{
          "properties": {
            "name": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "schema": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "display_name": {
              "type": "keyword"
            },
            "last_updated_timestamp": {
              "type": "date",
              "format": "epoch_second"
            },
            "description": {
              "type": "text",
              "analyzer": "simple"
            },
            "column_names": {
              "type":"text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "column_descriptions": {
              "type": "text",
              "analyzer": "simple"
            },
            "tags": {
              "type": "keyword"
            },
            "badges": {
              "type": "keyword"
            },
            "cluster": {
              "type": "text"
            },
            "database": {
              "type": "text",
              "analyzer": "simple",
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              }
            },
            "key": {
              "type": "keyword"
            },
            "total_usage":{
              "type": "long"
            },
            "unique_usage": {
              "type": "long"
            }
          }
        }
      }
    }
    """
)
