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
metadatalibrary and searchlibrary [here](/frontend/amundsen_application/api/utils/request_utils.py)

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

## Using Okta with Amundsen on K8s

Assumptions:

- You have access to okta (you can create a developer account for free!)
- You are using k8s to setup amundsen. See [amundsen-kube-helm](../../amundsen-kube-helm/README.md)

1. You need to have a stable DNS entry for amundsen-frontend that can be registered in okta.
    - for example in AWS you can setup route53
    I will assume for the rest of this tutorial that your stable uri is "http://amundsen-frontend"
2. You need to register amundsen in okta as an app. More info [here](https://developer.okta.com/blog/2018/07/12/flask-tutorial-simple-user-registration-and-login).
But here are specific instructions for amundsen:
    - At this time, I have only succesfully tested integration after ALL grants were checked.
    - Set the Login redirect URIs to: `http://amundsen-frontend/oidc_callback`
    - No need to set a logout redirect URI
    - Set the Initiate login URI to: `http://amundsen-frontend/`
        (This is where okta will take you if users click on amundsen via okta landing page)
    - Copy the Client ID and Client secret as you will need this later.
3. At present, there is no oidc build of the frontend. So you will need to build an oidc build yourself and upload it to, for example ECR, for use by k8s.
   You can then specify which image you want to use as a property override for your helm install like so:

   ```yaml
   frontEndServiceImage: 123.dkr.ecr.us-west-2.amazonaws.com/edmunds/amundsen-frontend:oidc-test
   ```

   Please see further down in this doc for more instructions on how to build frontend.
4. When you start up helm you will need to provide some properties. Here are the properties that need to be overridden for oidc to work:

    ```yaml
    oidcEnabled: true
    createOidcSecret: true
    OIDC_CLIENT_ID: YOUR_CLIENT_ID
    OIDC_CLIENT_SECRET: YOUR_SECRET_ID
    OIDC_ORG_URL: https://amundsen.okta.com
    OIDC_AUTH_SERVER_ID: default
    # You also will need a custom oidc frontend build too
    frontEndServiceImage: 123.dkr.ecr.us-west-2.amazonaws.com/edmunds/amundsen-frontend:oidc-test
    ```

## Building frontend with OIDC

1. Please look at [this guide](../developer_guide.md) for instructions on how to build a custom frontend docker image.
2. The only difference to above is that in your docker file you will want to add the following at the end. This will make sure its ready to go for oidc.
You can take alook at the public.Dockerfile as a reference.

```dockerfile
RUN pip3 install .[oidc]
ENV FRONTEND_SVC_CONFIG_MODULE_CLASS amundsen_application.oidc_config.OidcConfig
ENV APP_WRAPPER flaskoidc
ENV APP_WRAPPER_CLASS FlaskOIDC
ENV FLASK_OIDC_WHITELISTED_ENDPOINTS status,healthcheck,health
ENV SQLALCHEMY_DATABASE_URI sqlite:///sessions.db
```

Please also take a look at this blog [post](https://nirav-langaliya.medium.com/setup-oidc-authentication-with-lyft-amundsen-via-okta-eb0b89d724d3) for more detail.
