
import boto3
import json

bucket_name = 'careem-analytics'
region_name = 'eu-west-1'
session = boto3.session.Session(region_name=region_name)
s3 = session.resource('s3')

def read_s3_object(resource_key):
    obj = s3.Object(bucket_name,resource_key)
    stream_data = obj.get()['Body'].read().decode('utf-8')
    json_data = json.loads(stream_data)
    return json_data