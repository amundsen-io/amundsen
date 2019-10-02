# Flask configuration

After modifying any variable in [config.py](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/config.py) described in this document, be sure to rebuild your application with these changes.

**NOTE: This document is a work in progress and does not include 100% of features. We welcome PRs to complete this document**

## Mail Client Features
Amundsen has two features that leverage the custom mail client -- the feedback tool and notifications. For these features a custom implementation of [base_mail_client](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/base/base_mail_client.py) must be mapped to the `MAIL_CLIENT` configuration variable.

To fully enable these features in the UI, the application configuration variables for these features must also be set to true. Please see this [entry](application_config.md#mail-client-features) in our application configuration doc for further information.
