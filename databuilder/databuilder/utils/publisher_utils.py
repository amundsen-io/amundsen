# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

from os import listdir
from os.path import isfile, join
from typing import (
    Iterator, List, Set,
)

from pyhocon import ConfigTree

from databuilder.publisher.publisher_config_constants import PublisherConfigs


def chunkify_list(records: List[dict], chunk_size: int) -> Iterator[List[dict]]:
    """
    Generator to evenly split the input list into chunks
    """
    for index in range(0, len(records), chunk_size):
        yield records[index:index + chunk_size]


def create_props_param(record_dict: dict, additional_publisher_metadata_fields: dict) -> dict:
    """
    Create a dict of all the params for a given record
    """
    params = {}

    for k, v in {**record_dict, **additional_publisher_metadata_fields}.items():
        params[strip_unquoted_suffix(k)] = v

    return params


def get_props_body_keys(record_keys: list,
                        exclude_keys: Set,
                        additional_publisher_metadata_fields: dict) -> Set:
    """
    Returns the set of keys to be used in the props body of the merge statements
    :param record_keys:
    :param exclude_keys: set of excluded columns that do not need to be in properties (e.g: KEY, LABEL ...)
    :param additional_publisher_metadata_fields:
    """
    props_body_keys = set(record_keys) - exclude_keys
    formatted_keys = map(strip_unquoted_suffix, props_body_keys)
    return set(formatted_keys).union(additional_publisher_metadata_fields.keys())


def list_files(conf: ConfigTree, path_key: str) -> List[str]:
    """
    List files from directory
    :param conf:
    :param path_key:
    :return: List of file paths
    """
    if path_key not in conf:
        return []

    path = conf.get_string(path_key)
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]


def strip_unquoted_suffix(key: str) -> str:
    return key[:-len(PublisherConfigs.UNQUOTED_SUFFIX)] if key.endswith(PublisherConfigs.UNQUOTED_SUFFIX) else key
