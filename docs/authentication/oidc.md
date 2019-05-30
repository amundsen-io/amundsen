# OIDC (Keycloak) Authentication
Setting up end-to-end authentication using OIDC is fairly simple and can be done using a Flask wrapper i.e., [flaskoidc](https://github.com/verdan/flaskoidc).

`flaskoidc` leverages the Flask's `before_request` functionality to authenticate each request before passing that to
the views. It also accepts headers on each request if available in order to validate bearer token from incoming requests.

## Installation
Please refer to the [flaskoidc documentation](https://github.com/verdan/flaskoidc/blob/master/README.md)
for the installation and the configurations.

Note: You need to install and configure `flaskoidc` for each microservice of Amundsen
i.e., for frontendlibrary, metadatalibrary and searchlibrary in order to secure each of them.

## Amundsen Configuration
Once you have `flaskoidc` installed and configured for each microservice, please set the following environment variables:

- amundsenfrontendlibrary:
```bash
    APP_WRAPPER: flaskoidc
    APP_WRAPPER_CLASS: FlaskOIDC
```

- amundsenmetadatalibrary:
```bash
    FLASK_APP_MODULE_NAME: flaskoidc
    FLASK_APP_CLASS_NAME: FlaskOIDC
```

- amundsensearchlibrary: _(Needs to be implemented)_
```bash
    FLASK_APP_MODULE_NAME: flaskoidc
    FLASK_APP_CLASS_NAME: FlaskOIDC
```

By default `flaskoidc` whitelist the healthcheck URLs, to not authenticate them. In case of metadatalibrary and searchlibrary
we may want to whitelist the healthcheck APIs explicitly using following environment variable.

```bash
    FLASK_OIDC_WHITELISTED_ENDPOINTS: 'api.healthcheck'
```

## Setting Up Request Headers
To communicate securely between the microservices, you need to pass the bearer token from frontend in each request
to metadatalibrary and searchlibrary. This should be done using `REQUEST_HEADERS_METHOD` config variable in frontendlibrary.

- Define a function to add the bearer token in each request in your config.py:
```python
def get_access_headers(app):
    """
    Function to retrieve and format the Authorization Headers
    that can be passed to various microservices who are expecting that.
    :param oidc: OIDC object having authorization information
    :return: A formatted dictionary containing access token
    as Authorization header.
    """
    try:
        access_token = app.oidc.get_access_token()
        return {'Authorization': 'Bearer {}'.format(access_token)}
    except Exception:
        return None
```

- Set the method as the request header method in your config.py:
```python
REQUEST_HEADERS_METHOD = get_access_headers
```

This function will be called using the current `app` instance to add the headers in each request when calling any endpoint of
metadatalibrary and searchlibrary [here](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/api/utils/request_utils.py)

## Setting Up Auth User Method
In order to get the current authenticated user (which is being used in Amundsen for many operations), we need to set
`AUTH_USER_METHOD` config variable in frontendlibrary.
This function should return email address, user id and any other required information.

- Define a function to fetch the user information in your config.py:
```python
def get_auth_user(app):
    """
    Retrieves the user information from oidc token, and then makes
    a dictionary 'UserInfo' from the token information dictionary.
    We need to convert it to a class in order to use the information
    in the rest of the Amundsen application.
    :param app: The instance of the current app.
    :return: A class UserInfo
    """
    from flask import g
    user_info = type('UserInfo', (object,), g.oidc_id_token)
    # noinspection PyUnresolvedReferences
    user_info.user_id = user_info.preferred_username
    return user_info
```

- Set the method as the auth user method in your config.py:
```python
AUTH_USER_METHOD = get_auth_user
```

Once done, you'll have the end-to-end authentication in Amundsen without any proxy or code changes.
