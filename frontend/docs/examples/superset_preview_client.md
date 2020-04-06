# Overview

Amundsen's data preview feature requires that developers create a custom implementation of `base_preview_client` for requesting that data. This feature assists with data discovery by providing the end user the option to view a sample of the actual resource data so that they can verify whether or not they want to transition into exploring that data, or continue their search.

[Apache Superset](https://github.com/apache/incubator-superset) is an open-source business intelligence tool that can be used for data exploration. Amundsen's data preview feature was created with Superset in mind, and it is what we leverage internally at Lyft to support the feature. This document provides some insight into how to configure Amundsen's frontend application to leverage Superset for data previews.

## Implementation

Implement the `base_superset_preview_client` to make a request to an instance of Superset.

### Shared Logic
[`base_superset_preview_client`](https://github.com/lyft/amundsenfrontendlibrary/tree/master/amundsen_application/base/base_superset_preview_client.py) implements `get_preview_data()` of `base_preview_client` with the minimal logic for this use case.

It updates the headers for the request if `optionalHeaders` are passed in `get_preview_data()`
```
# Clone headers so that it does not mutate instance's state
headers = dict(self.headers)

# Merge optionalHeaders into headers
if optionalHeaders is not None:
    headers.update(optionalHeaders)
```

It verifies the shape of the data before returning it to the application. If the data does not match the `PreviewDataSchema`, the request will fail.
```
# Verify and return the results
response_dict = response.json()
columns = [ColumnItem(c['name'], c['type']) for c in response_dict['columns']]
preview_data = PreviewData(columns, response_dict['data'])
data, errors = PreviewDataSchema().dump(preview_data)
if not errors:
    payload = jsonify({'preview_data': data})
    return make_response(payload, response.status_code)
else:
    return make_response(jsonify({'preview_data': {}}), HTTPStatus.INTERNAL_SERVER_ERROR)
```

### Custom Logic
`base_superset_preview_client` has an abstract method `post_to_sql_json()`. This method will contain whatever custom logic is needed to make a successful request to the `sql_json` enpoint based on the protections you have configured on this endpoint on your instance of Superset. For example, this may be where you have to append other values to the headers, or generate SQL queries based on your use case.

See the following [`example_superset_preview_client`](https://github.com/lyft/amundsenfrontendlibrary/tree/master/amundsen_application/base/examples/example_superset_preview_client.py) for an example implementation of `base_superset_preview_client` and `post_to_sql_json()`. This example assumes a local instance of Superset running on port 8088 with no security, authentication, or authorization configured on the endpoint.


## Usage

Under the `[preview_client]` group, point the `table_preview_client_class` entry point in your local `setup.py` to your custom class.

```
entry_points="""
    ...

    [preview_client]
    table_preview_client_class = amundsen_application.base.examples.example_superset_preview_client:SupersetPreviewClient
"""
```

Run `python3 setup.py install` in your virtual environment and restart the application for the entry point changes to take effect
