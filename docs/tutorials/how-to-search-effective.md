# How to search Amundsen effectively

The goal of this tutorial is to provide a few tips on how to search for datasets effectively in Amundsen. 

## Overview

Amundsen currently indexes three types of entities: tables, people, and dashboards. This tutorial mostly covers how to search for a table entity effectively.

We will cover other entities in the future.

## General Search

Once the users are on the Amundsen home page,  the users could search for any random information in the search bar. In the backend, the search system will use the same query term from users and search across three different entities (tables, people, and dashboards) and return the results with the highest ranking. For Table search, it will search across different fields, including table name, schema name, table or column descriptions, tags and etc. Amundsen also supports typeahead search which will search in the backend as soon as users enter new characters. 


Tips:

- If you know the full table name (e.g. schema.table), try to search with that full table name, which will provide as the top result in general.
- If you are unsure of the table name, search with `word1 word2` with space in between. For example, if your table's name is `test.test_rides`  but you don't know the exact table name but only know the table name includes test and rides, please search with `test rides` (space in between). In this case, Amundsen will return tables that match either test or rides and union the result together based on the search algorithm ranking.
- If you know your table name but don't know the schema of the table name, you could search with `word1_word2`. For example, if you know your table name is `test_rides`, please search with `test_rides` that will only return the table matched that given name.

## Advanced Search

If you want to do the traditional faceted search, which will allow users to apply multiple filters, you could try out the advanced search. Currently, only the table entity is supported with the advanced search. But we plan to add the support for the dashboard entity as well in the near future.

You could use wildcard in the search box as well. In the above example, the users put `rides*`  on the table box. This will search across all the tables that have rides* as table name from different databases, including bigquery/druid/hive/presto/rs, etc.

If you want to narrow down the search results, you could put more filters. In the above example, the users try to search a table name that is `rides*`, which has beta as the badge. Once the search is finished, you could see only one table matches the criteria (test.rides in this case). 

## Searching Ranking Algorithm Demystified

Currently, Amundsen provides the same search ranking for all the different personas. It ranks the table based on the query count in the presto search query log from the past 90 days at Lyft. It could be different based on your company's setup.

## Try out different search heuristic

You could always try out different search heuristic using the kibana devtools.

For example for table, you could use:
```
GET table_search_index/_search
{
  "query": {
              "function_score": {
                "query": {
                    "multi_match": {
                        "query": "$term",
                        "fields": ["display_name^1000",
                                   "name.raw^75",
                                   "name^5",
                                   "schema^3",
                                   "description^3",
                                   "column_names^2",
                                   "column_descriptions",
                                   "tags",
                                   "badges",
                                   "programmatic_descriptions"]
                    }
                },
                "field_value_factor": {
                    "field": "total_usage",
                    "modifier": "log2p"
                }
            }
  }
}
```

The result will be ranked with certain weight based on total usage. It is the same as the following with painless script:
```
"function_score": {
    "query": {
        "multi_match": {
            "query": query_term,
            "fields": ["display_name^1000",
                       "name.raw^75",
                       "name^5",
                       "schema^3",
                       "description^3",
                       "column_names^2",
                       "column_descriptions",
                       "tags",
                       "badges",
                       "programmatic_descriptions"],
        }
    },
    "functions": [
        {
            "script_score": {
                "script": "def scores = 0; scores = doc['total_usage'].value; return _score * Math.log10(2 + scores); }"

            }
        }
    ]
}
```

If you want to boot the search result that has certain badge:
```
"function_score": {
    "query": {
        "multi_match": {
            "query": query_term,
            "fields": ["display_name^1000",
                       "name.raw^75",
                       "name^5",
                       "schema^3",
                       "description^3",
                       "column_names^2",
                       "column_descriptions",
                       "tags",
                       "badges",
                       "programmatic_descriptions"],
        }
    },
    "functions": [
        {
            "script_score": {
                "script": "def scores = 0; scores = doc['total_usage'].value; if (doc['badges'].value == "
                          "'$badge_for_boost') {return _score * Math.log10(2 + scores) "
                          "* 1.5} else{ return _score * Math.log10(2 + scores); }"

            }
        }
    ]
}
```

In this case, the table with a badge ($badge_for_boost or replace with your own badge), the search ranking score will get boosted.

For dashboard, you could try out the following:
```
GET dashboard_search_index/_search
{
  "query": {
    "function_score": {
                "query": {
                    "multi_match": {
                        "query": "$search-term",
                        "fields": ["name.raw^75",
                                   "name^7",
                                   "group_name.raw^15",
                                   "group_name^7",
                                   "description^3",
                                   "query_names^3"]
                    }
                },
                "field_value_factor": {
                    "field": "total_usage",
                    "modifier": "log2p"
                }
            }
  }
}
```

Hope this tutorial gives you some ideas on how the search works.
