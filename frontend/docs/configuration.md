# Configuration

## Flask
The default Flask application uses a [LocalConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) that looks for the metadata and search services running on localhost. In order to use different end point, you need to create a custom config class suitable for your use case. Once the config class has been created, it can be referenced via the [environment variable](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/wsgi.py#L5): `FRONTEND_SVC_CONFIG_MODULE_CLASS`

For more examples of how to leverage the Flask configuration for specific features, please see this [extended doc](flask_config.md).

For more information on Flask configurations, please reference the official Flask [documentation](http://flask.pocoo.org/docs/1.0/config/#development-production).


## React Application
### Application Config
Certain features of the React application import variables from an [AppConfig](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config.ts#L5) object. The configuration can be customized by modifying [config-custom.ts](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config-custom.ts).

For examples of how to leverage the application configuration for specific features, please see this [extended doc](application_config.md).

### Custom Fonts & Styles
Fonts and css variables can be customized by modifying [fonts-custom.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_fonts-custom.scss) and
[variables-custom.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_variables-custom.scss).


## Authentication
Authentication can be hooked within Amundsen using either wrapper class or using proxy to secure the microservices
on the nginx/server level. Following are the ways to setup the end-to-end authentication.
- [OIDC / Keycloak](authentication/oidc.md)
