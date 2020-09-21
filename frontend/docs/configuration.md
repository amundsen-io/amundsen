# Configuration

## Flask
The default Flask application uses a [LocalConfig](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) that looks for the metadata and search services running on localhost. In order to use different end point, you need to create a custom config class suitable for your use case. Once the config class has been created, it can be referenced via the [environment variable](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/wsgi.py#L5): `FRONTEND_SVC_CONFIG_MODULE_CLASS`

For more examples of how to leverage the Flask configuration for specific features, please see this [extended doc](flask_config.md).

For more information on Flask configurations, please reference the official Flask [documentation](http://flask.pocoo.org/docs/1.0/config/#development-production).


## React Application
### Application Config
Certain features of the React application import variables from an [AppConfig](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config.ts#L5) object. The configuration can be customized by modifying [config-custom.ts](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config-custom.ts).

For examples of how to leverage the application configuration for specific features, please see this [extended doc](application_config.md).

### Custom Fonts & Styles
Fonts and css variables can be customized by modifying [fonts-custom.scss](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_fonts-custom.scss) and
[variables-custom.scss](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_variables-custom.scss).


## Python Entry Points
The application also leverages [python entry points](https://packaging.python.org/specifications/entry-points/) for custom features.
In your local `setup.py`, point the entry points detailed below to custom classes or methods that have to be implemented for a given feature.
Run `python3 setup.py install` in your virtual environment and restart the application for the entry point changes to take effect.

```
entry_points="""
    [action_log.post_exec.plugin]
    analytic_clients_action_log = path.to.file:custom_action_log_method

    [preview_client]
    table_preview_client_class = amundsen_application.base.examples.example_superset_preview_client:SupersetPreviewClient

    [announcement_client]
    announcement_client_class = amundsen_application.base.examples.example_announcement_client:SQLAlchemyAnnouncementClient
"""
```

### Action Logging
Create a custom method to handle action logging. Under the `[ action_log.post_exec.plugin]` group, point the `analytic_clients_action_log` entry point in your local `setup.py` to that method.

### Preview Client
Create a custom implementation of [base_preview_client](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/base/base_preview_client.py). Under the `[preview_client]` group, point the `table_preview_client_class` entry point in your local `setup.py` to that class.

For those who use [Apache Superset](https://github.com/apache/incubator-superset) for data exploration, see [this doc](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/docs/examples/superset_preview_client.md) for how to implement a preview client for Superset.

### Announcement Client
Create a custom implementation of [base_announcement_client](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/base/base_announcement_client.py). Under the `[announcement_client]` group, point the `announcement_client_class` entry point in your local `setup.py` to that class.

Currently Amundsen does not own the input and storage of announcements. Consider having the client fetch announcement information from an external web feed.

## Authentication
Authentication can be hooked within Amundsen using either wrapper class or using proxy to secure the microservices
on the nginx/server level. Following are the ways to setup the end-to-end authentication.
- [OIDC / Keycloak](authentication/oidc.md)
