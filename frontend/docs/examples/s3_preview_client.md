# Overview

Amundsen's data preview feature requires that developers create a custom implementation of `base_preview_client` for requesting that data. This feature assists with data discovery by providing the end user the option to view a sample of the actual resource data so that they can verify whether or not they want to transition into exploring that data, or continue their search.

[S3](https://aws.amazon.com/s3/) is AWS block storage and is used in this scenario for storing precomputed preview data.

## Implementation

Implement the `base_s3_preview_client` to make a request to AWS using [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) to fetch your preview data. 
Your preview data needs to already be stored in S3 for this to work. 
You can take a look at `example_s3_json_preview_client` to see a working implementation that fetches JSON files.


## Usage

To use a preview client set these environment variables in your deployment.

- `PREVIEW_CLIENT_ENABLED`: `true`
- `PREVIEW_CLIENT`: `{python path to preview client class}` (ex: `amundsen_application.base.examples.example_s3_json_preview_client.S3JSONPreviewClient` if you are using the JSON example client)
- `PREVIEW_CLIENT_S3_BUCKET`: `{S3 bucket where the preview data is stored}`