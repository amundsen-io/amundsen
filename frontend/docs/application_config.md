# Application configuration

This document describes how to leverage the frontend service's application configuration to configure particular features. After modifying the `AppConfigCustom` object in [config-custom.ts](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config-custom.ts) in the ways described in this document, be sure to rebuild your application with these changes.

**NOTE: This document is a work in progress and does not include 100% of features. We welcome PRs to complete this document**

## Badge Config
Badges are a special type of tag that cannot be edited through the UI. 

`BadgeConfig` can be used to customize the text and color of badges. This config defines a mapping of badge name to a `BadgeStyle` and optional `displayName`. Badges that are not defined will default to use the `BadgeStyle.default` style and `displayName` use the badge name with any `_` or `-` characters replaced with a space.   

## Browse Tags Feature

_TODO: Please add doc_

## Custom Logo

1. Add your logo to the folder in `amundsen_application/static/images/`.
2. Set the the `logoPath` key on the  to the location of your image.

## Google Analytics

_TODO: Please add doc_

## Index Users
In Amundsen, users themselves are data resources and user metadata helps to facilitate network based discovery. When users are indexed they will show up in search results, and selecting a user surfaces a profile page that displays that user's relationships with different data resources.

After ingesting user metadata into the search and metadata services, set `IndexUsersConfig.enabled` to `true` on the application configuration to display the UI for the aforementioned features. 

## Mail Client Features
Amundsen has two features that leverage the custom mail client -- the feedback tool and notifications.

As these are optional features, our `MailClientFeaturesConfig` can be used to hide/display any UI related to these features:
1. Set `MailClientFeaturesConfig.feedbackEnabled` to `true` in order to display the `Feedback` component in the UI.
2. Set `MailClientFeaturesConfig.notificationsEnabled` to `true` in order to display the optional UI for users to request more information about resources on the `TableDetail` page.

For information about how to configure a custom mail
client, please see this [entry](flask_config.md#mail-client-features) in our flask configuration doc.

## Navigation Links

_TODO: Please add doc_

## Resource Configurations

### Datasets
We provide a `datasets` option on our `ResourceConfig`. This can be used for the following customizations:

#### Custom Icons
You can configure custom icons to be used throughout the UI when representing datasets from particular sources/databases. On the `ResourceConfig.datasets` object, add an entry with the `id` used to reference that database and set the `iconClass`. This `iconClass` should be defined in [icons.scss](https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_icons.scss).

#### Display Names
You can configure a specific display name to be used throughout the UI when representing datasets from particular sources/databases. On the `ResourceConfig.datasets` object, add an entry with the `id` used to reference that database and set the `displayName`.

## Table Lineage

_TODO: Please add doc_

## Table Profile

_TODO: Please add doc*_
