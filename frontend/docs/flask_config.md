# Flask configuration

After modifying any variable in [config.py](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) described in this document, be sure to rebuild your application with these changes.

**NOTE: This document is a work in progress and does not include 100% of features. We welcome PRs to complete this document**

## Custom Routes
In order to add any custom Flask endpoints to Amundsen's frontend application, configure a function on the `INIT_CUSTOM_ROUTES` variable. This function takes the created Flask application and can leverage Flask's [add_url_rule](https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.add_url_rule) method to add custom routes.

Example: Setting `INIT_CUSTOM_ROUTES` to the `init_custom_routes` method below will expose a `/custom_route` endpoint on the frontend application.
```bash
def init_custom_routes(app: Flask) -> None:
  app.add_url_rule('/custom_route', 'custom_route', custom_route)

def custom_route():
  pass
```

## Mail Client Features
Amundsen has two features that leverage the custom mail client -- the feedback tool and notifications. For these features a custom implementation of [base_mail_client](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/base/base_mail_client.py) must be mapped to the `MAIL_CLIENT` configuration variable.

To fully enable these features in the UI, the application configuration variables for these features must also be set to true. Please see this [entry](application_config.md#mail-client-features) in our application configuration doc for further information.
