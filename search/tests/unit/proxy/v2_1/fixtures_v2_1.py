# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

TERM_FILTERS_QUERY = {
    "bool": {
        "must": [
            {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "name": {
                                    "query": "mock_feature",
                                    "fuzziness": "AUTO",
                                    "boost": 5,
                                }
                            }
                        },
                        {
                            "match": {
                                "description": {
                                    "query": "mock_feature",
                                    "fuzziness": "AUTO",
                                    "boost": 1.5,
                                }
                            }
                        },
                        {
                            "match": {
                                "badges": {"query": "mock_feature", "fuzziness": "AUTO"}
                            }
                        },
                        {
                            "match": {
                                "tags": {"query": "mock_feature", "fuzziness": "AUTO"}
                            }
                        },
                        {
                            "match": {
                                "feature_group": {
                                    "query": "mock_feature",
                                    "fuzziness": "AUTO",
                                    "boost": 3,
                                }
                            }
                        },
                        {"match": {"version": {"query": "mock_feature"}}},
                        {
                            "match": {
                                "entity": {
                                    "query": "mock_feature",
                                    "fuzziness": "AUTO",
                                    "boost": 2,
                                }
                            }
                        },
                        {"match": {"status": {"query": "mock_feature"}}},
                    ]
                }
            }
        ],
        "should": [{"rank_feature": {"field": "usage.total_usage", "boost": 10}}],
        "filter": [
            {"wildcard": {"badges.keyword": "pii"}},
            {
                "bool": {
                    "should": [
                        {"wildcard": {"feature_group.keyword": "test_group"}},
                        {"wildcard": {"feature_group.keyword": "mock_group"}},
                    ],
                    "minimum_should_match": 1,
                }
            },
        ],
    }
}
TERM_QUERY = {
    "bool": {
        "must": [
            {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "name": {
                                    "query": "mock_table",
                                    "fuzziness": "AUTO",
                                    "boost": 5,
                                }
                            }
                        },
                        {
                            "match": {
                                "description": {
                                    "query": "mock_table",
                                    "fuzziness": "AUTO",
                                    "boost": 1.5,
                                }
                            }
                        },
                        {
                            "match": {
                                "badges": {"query": "mock_table", "fuzziness": "AUTO"}
                            }
                        },
                        {
                            "match": {
                                "tags": {"query": "mock_table", "fuzziness": "AUTO"}
                            }
                        },
                        {
                            "match": {
                                "schema": {
                                    "query": "mock_table",
                                    "fuzziness": "AUTO",
                                    "boost": 3,
                                }
                            }
                        },
                        {
                            "match": {
                                "columns.general": {
                                    "query": "mock_table",
                                    "fuzziness": "AUTO",
                                    "boost": 2,
                                }
                            }
                        },
                        {
                            "match": {
                                "column_descriptions": {
                                    "query": "mock_table",
                                    "fuzziness": "AUTO",
                                }
                            }
                        },
                    ]
                }
            }
        ],
        "should": [
            {"rank_feature": {"field": "usage.total_usage", "boost": 10}},
            {"rank_feature": {"field": "usage.unique_usage", "boost": 10}},
        ],
    }
}

FILTER_QUERY = {
    "bool": {
        "filter": [
            {
                "bool": {
                    "should": [{"wildcard": {"name.keyword": "mock_dashobard_*"}}],
                    "minimum_should_match": 1,
                }
            },
            {
                "bool": {
                    "should": [
                        {"wildcard": {"group_name.keyword": "test_group"}},
                        {"wildcard": {"group_name.keyword": "mock_group"}},
                    ],
                    "minimum_should_match": 1,
                }
            },
            {"wildcard": {"tags.keyword": "tag_*"}},
            {"wildcard": {"tags.keyword": "tag_2"}},
        ]
    }
}

RESPONSE_1 = [
    {
        "took": 10,
        "timed_out": False,
        "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 2, "relation": "eq"},
            "max_score": 804.52716,
            "hits": [
                {
                    "_index": "table_search_index",
                    "_type": "table",
                    "_id": "mock_id_1",
                    "_score": 804.52716,
                    "_source": {
                        "badges": ["pii", "beta"],
                        "cluster": "mock_cluster",
                        "column_descriptions": [
                            "mock_col_desc_1",
                            "mock_col_desc_2",
                            "mock_col_desc_3",
                        ],
                        "columns": ["mock_col_1", "mock_col_2", "mock_col_3"],
                        "database": "mock_db",
                        "description": "mock table description",
                        "display_name": "mock_schema.mock_table_1",
                        "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                        "last_updated_timestamp": 1635831717,
                        "name": "mock_table_1",
                        "programmatic_descriptions": [],
                        "schema": "mock_schema",
                        "schema_description": None,
                        "tags": ["mock_tag_1", "mock_tag_2", "mock_tag_3"],
                        "total_usage": 74841,
                        "unique_usage": 457,
                        "resource_type": "table",
                    },
                },
                {
                    "_index": "table_search_index",
                    "_type": "table",
                    "_id": "mock_id_2",
                    "_score": 9.104584,
                    "_source": {
                        "badges": [],
                        "cluster": "mock_cluster",
                        "column_descriptions": [
                            "mock_col_desc_1",
                            "mock_col_desc_2",
                            "mock_col_desc_3",
                        ],
                        "columns": ["mock_col_1", "mock_col_2", "mock_col_3"],
                        "database": "mock_db",
                        "description": "mock table description",
                        "display_name": "mock_schema.mock_table_2",
                        "key": "mock_db://mock_cluster.mock_schema/mock_table_2",
                        "last_updated_timestamp": 1635831717,
                        "name": "mock_table_2",
                        "programmatic_descriptions": [],
                        "schema": "mock_schema",
                        "schema_description": None,
                        "tags": ["mock_tag_4", "mock_tag_5", "mock_tag_6"],
                        "total_usage": 4715,
                        "unique_usage": 254,
                        "resource_type": "table",
                    },
                },
            ],
        },
        "status": 200,
    },
    {
        "took": 1,
        "timed_out": False,
        "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 0, "relation": "eq"},
            "max_score": None,
            "hits": [],
        },
        "status": 200,
    },
]


RESPONSE_2 = [
    {
        "took": 12,
        "timed_out": False,
        "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 2, "relation": "eq"},
            "max_score": 771.9865,
            "hits": [
                {
                    "_index": "table_search_index",
                    "_type": "table",
                    "_id": "mock_id_1",
                    "_score": 804.52716,
                    "_source": {
                        "badges": ["pii", "beta"],
                        "cluster": "mock_cluster",
                        "column_descriptions": [
                            "mock_col_desc_1",
                            "mock_col_desc_2",
                            "mock_col_desc_3",
                        ],
                        "columns": ["mock_col_1", "mock_col_2", "mock_col_3"],
                        "database": "mock_db",
                        "description": "mock table description",
                        "display_name": "mock_schema.mock_table_1",
                        "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                        "last_updated_timestamp": 1635831717,
                        "name": "mock_table_1",
                        "programmatic_descriptions": [],
                        "schema": "mock_schema",
                        "schema_description": None,
                        "tags": ["mock_tag_1", "mock_tag_2", "mock_tag_3"],
                        "total_usage": 74841,
                        "unique_usage": 457,
                        "resource_type": "table",
                    },
                },
                {
                    "_index": "table_search_index",
                    "_type": "table",
                    "_id": "mock_id_2",
                    "_score": 9.104584,
                    "_source": {
                        "badges": [],
                        "cluster": "mock_cluster",
                        "column_descriptions": [
                            "mock_col_desc_1",
                            "mock_col_desc_2",
                            "mock_col_desc_3",
                        ],
                        "columns": ["mock_col_1", "mock_col_2", "mock_col_3"],
                        "database": "mock_db",
                        "description": "mock table description",
                        "display_name": "mock_schema.mock_table_2",
                        "key": "mock_db://mock_cluster.mock_schema/mock_table_2",
                        "last_updated_timestamp": 1635831717,
                        "name": "mock_table_2",
                        "programmatic_descriptions": [],
                        "schema": "mock_schema",
                        "schema_description": None,
                        "tags": ["mock_tag_4", "mock_tag_5", "mock_tag_6"],
                        "total_usage": 4715,
                        "unique_usage": 254,
                        "resource_type": "table",
                    },
                },
            ],
        },
        "status": 200,
    },
    {
        "took": 6,
        "timed_out": False,
        "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 1, "relation": "eq"},
            "max_score": 61.40606,
            "hits": [
                {
                    "_index": "user_search_index",
                    "_type": "user",
                    "_id": "mack_user_id",
                    "_score": 61.40606,
                    "_source": {
                        "key": "mock_user@amundsen.com",
                        "employee_type": "",
                        "first_name": "Allison",
                        "name": "Allison Suarez Miranda",
                        "github_username": "allisonsuarez",
                        "is_active": True,
                        "last_name": "Suarez Miranda",
                        "manager_email": "mock_manager@amundsen.com",
                        "role_name": "SWE",
                        "slack_id": "",
                        "team_name": "Amundsen",
                        "total_follow": 0,
                        "total_own": 1,
                        "total_read": 0,
                        "resource_type": "user",
                    },
                }
            ],
        },
        "status": 200,
    },
    {
        "took": 8,
        "timed_out": False,
        "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
        "hits": {
            "total": {"value": 3, "relation": "eq"},
            "max_score": 62.66787,
            "hits": [
                {
                    "_index": "feature_search_index",
                    "_type": "feature",
                    "_id": "mock_feat_id",
                    "_score": 62.66787,
                    "_source": {
                        "availability": None,
                        "badges": [],
                        "description": "mock feature description",
                        "entity": None,
                        "feature_group": "fg_2",
                        "name": "feature_1",
                        "key": "none/feature_1/1",
                        "last_updated_timestamp": 1525208316,
                        "status": "active",
                        "tags": [],
                        "total_usage": 0,
                        "version": 1,
                        "resource_type": "feature",
                    },
                },
                {
                    "_index": "feature_search_index",
                    "_type": "feature",
                    "_id": "mock_feat_id_2",
                    "_score": 62.66787,
                    "_source": {
                        "availability": None,
                        "badges": [],
                        "description": "mock feature description",
                        "entity": None,
                        "feature_group": "fg_2",
                        "name": "feature_2",
                        "key": "fg_2/feature_2/1",
                        "last_updated_timestamp": 1525208316,
                        "status": "active",
                        "tags": [],
                        "total_usage": 10,
                        "version": 1,
                        "resource_type": "feature",
                    },
                },
                {
                    "_index": "feature_search_index",
                    "_type": "feature",
                    "_id": "mock_feat_id_3",
                    "_score": 62.66787,
                    "_source": {
                        "availability": None,
                        "badges": ["pii"],
                        "description": "mock feature description",
                        "entity": None,
                        "feature_group": "fg_3",
                        "name": "feature_3",
                        "key": "fg_3/feature_3/2",
                        "last_updated_timestamp": 1525208316,
                        "status": "active",
                        "tags": [],
                        "total_usage": 3,
                        "version": 2,
                        "resource_type": "feature",
                    },
                },
            ],
        },
        "status": 200,
    },
]

ES_RESPONSE_HIGHLIGHTED = {
    "took": 10,
    "timed_out": False,
    "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0},
    "hits": {
        "total": {"value": 2, "relation": "eq"},
        "max_score": 804.52716,
        "hits": [
            {
                "_index": "table_search_index",
                "_type": "table",
                "_id": "mock_id_1",
                "_score": 804.52716,
                "_source": {
                    "badges": ["pii", "beta"],
                    "cluster": "mock_cluster",
                    "column_descriptions": [
                        "mock_col_desc_1",
                        "mock_col_desc_2",
                        "mock_col_desc_3",
                    ],
                    "columns": ["mock_col_1", "mock_col_2", "mock_col_3"],
                    "database": "mock_db",
                    "description": "mock table description",
                    "display_name": "mock_schema.mock_table_1",
                    "key": "mock_db://mock_cluster.mock_schema/mock_table_1",
                    "last_updated_timestamp": 1635831717,
                    "name": "mock_table_1",
                    "programmatic_descriptions": [],
                    "schema": "mock_schema",
                    "schema_description": None,
                    "tags": ["mock_tag_1", "mock_tag_2", "mock_tag_3"],
                    "total_usage": 74841,
                    "unique_usage": 457,
                    "resource_type": "table",
                },
                "highlight": {
                    "name": ["<em>mock</em>_table_1"],
                    "columns.general": [
                        "<em>mock</em>_col_1",
                        "<em>mock</em>_col_2",
                        "<em>mock</em>_col_3",
                    ],
                    "description": ["<em>mock</em> table description"],
                },
            },
        ],
    },
    "status": 200,
}
