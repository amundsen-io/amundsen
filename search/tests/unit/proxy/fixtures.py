# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

TERM_FILTERS_QUERY = {
    "bool": {
        "should": [
            {
                "multi_match": {
                    "query": "mock_feature",
                    "fields": [
                        "feature_name.raw^25",
                        "feature_name^7",
                        "feature_group.raw^15",
                        "feature_group^7",
                        "version^7",
                        "description^3",
                        "status",
                        "entity",
                        "tags",
                        "badges"
                    ],
                    "type": "most_fields"
                }
            }
        ],
        "filter": [
            {
                "wildcard": {
                    "badges": "pii"
                }
            },
            {
                "bool": {
                    "should": [
                        {
                            "wildcard": {
                                "feature_group.raw": "test_group"
                            }
                        },
                        {
                            "wildcard": {
                                "feature_group.raw": "mock_group"
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            }
        ]
    }
}

TERM_QUERY = {
    "bool": {
        "should": [
            {
                "multi_match": {
                    "query": "mock_table",
                    "fields": [
                        "display_name^1000",
                        "name.raw^75",
                        "name^5",
                        "schema^3",
                        "description^3",
                        "column_names^2",
                        "column_descriptions",
                        "tags",
                        "badges",
                        "programmatic_descriptions"
                    ],
                    "type": "most_fields"
                }
            }
        ]
    }
}

FILTER_QUERY = {
    "bool": {
        "filter": [
            {
                "bool": {
                    "should": [
                        {
                            "wildcard": {
                                "name.raw": "mock_dashobard_*"
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            {
                "bool": {
                    "should": [
                        {
                            "wildcard": {
                                "group_name.raw": "test_group"
                            }
                        },
                        {
                            "wildcard": {
                                "group_name.raw": "mock_group"
                            }
                        }
                    ],
                    "minimum_should_match": 1
                }
            },
            {
                "wildcard": {
                    "tags": "tag_*"
                }
            },
            {
                "wildcard": {
                    "tags": "tag_2"
                }
            }
        ]
    }
}