# Copyright Contributors to the Amundsen project.
# SPDX-License-Identifier: Apache-2.0

import boto3
import json
from http import HTTPStatus
from typing import Any, Iterable
from flasgger import swag_from
from flask_restful import Resource, reqparse


bucket_name = 'careem-analytics'
region_name = 'eu-west-1'
session = boto3.session.Session(region_name=region_name)
s3 = session.resource('s3')


class GetFilterConfigAPI(Resource):
    """
    Get Filter Config API
    """
    
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser(bundle_errors=True)
        super(GetFilterConfigAPI, self).__init__()

    @swag_from('swagger_doc/filter_config/get_filter_config.yml')
    def get(self) -> Iterable[Any]:
        """
        Fetch filter config results.

        :return: list of resources config results. Can be empty if no matches.
        """
        try:
            data = self._read_config_from_s3(['table','service','dashboard','app_event'])
            return data, HTTPStatus.OK
        except RuntimeError:
            err_msg = 'Exception encountered while processing get request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    def read_s3_object(self,resource_key):
        
        obj = s3.Object(bucket_name,resource_key)
        stream_data = obj.get()['Body'].read().decode('utf-8')
        json_data = json.loads(stream_data)
        return json_data

    def _read_config_from_s3(self,resource_config_keys):
        data = {
            "table": {
                "filterCategories" : []
            },
            "service": {
                "filterCategories" : []
            },
            "dashboard": {
                "filterCategories" : []
            },
            "events": {
                "filterCategories" : []
            },

        }

        for resource_key in resource_config_keys:
            resource_filter_config = self.read_s3_object(resource_key="filte-config/" + resource_key + "_filters_data.json")
            if resource_key == 'app_event': 
                data['events']['filterCategories'] = resource_filter_config['config']
            else:
                data[resource_key]['filterCategories'] = resource_filter_config['config']
        return data
            