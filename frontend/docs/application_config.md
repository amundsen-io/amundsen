# Application configuration

This document describes how to leverage the frontend service's application configuration to configure particular features. After modifying the `AppConfigCustom` object in [config-custom.ts](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-custom.ts) in the ways described in this document, be sure to rebuild your application. All default config values are set in the [config-default.ts](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-default.ts) file.

## Analytics

Amundsen supports pluggable user behavior analytics via the [analytics](https://github.com/DavidWells/analytics) library.

To emit analytics to a given destination, you must use one of the provided plugins (open a PR if you need to install a different vendor), then specify it the config passing the configuration of your account. Multiple destinations are supported if you wish to emit to multiple backends simultaneously.

We provide out of the box support for Mixpanel, Segment and Google Analytics. All [`@analytics/` plugins](https://github.com/DavidWells/analytics#analytic-plugins) are potentially supported, but you must first install the plugin: `npm install @analytics/<provider>` and send us a PR with it before you can use it.

### Examples
For example, to use Google analytics, you must add the import at the top of your `config-custom.ts` file: `import googleAnalytics from '@analytics/google-analytics';`, then add this config block:

```js
analytics: {
  plugins: [
    googleAnalytics({
      trackingId: '<YOUR_UA_CODE>',
      sampleRate: 100
    }),
  ],
}
```

## Announcements

Announcements is a feature that allows to disclose new features, changes or any other news to Amundsen's users using a panel in the homepage.

<figure>
  <img src='img/announcements_feature.png' width='50%' />
  <figcaption>Announcements in the homepage</figcaption>
</figure>

To enable this feature, change the `announcements.enabled` boolean value by overriding it on [config-custom.ts](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-custom.ts). Once activated, an "Announcements" link will be available in the global navigation, and a new list of announcements will show up on the right sidebar on the Homepage.

Refer to [announcement_client.md](https://github.com/amundsen-io/amundsen/blob/main/frontend/docs/examples/announcement_client.md) for information about fetching announcements.

### Examples
To turn announcements on, change the flag as below:
```js
announcements: {
  enabled: true,
},
```

## Badges

Badges are a special type of tag that cannot be edited through the UI.

The [`BadgeStyleConfig` type](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-types.ts#L273) can be used to customize the text and color of badges. This config defines a mapping of badge name to a [`BadgeStyle`](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-types.ts#L264) and optional `displayName`. Badges that are not defined will default to use the `BadgeStyle.default` style and `displayName` use the badge name with any `_` or `-` characters replaced with a space.

### Examples
Check below to see how to set two badges for two generic 'alpha' and 'beta' badges:
```js
alpha: {
  style: BadgeStyle.DEFAULT,
  displayName: "Alpha",
},
beta: {
  style: BadgeStyle.DEFAULT,
  displayName: "Beta",
},
```

## Browse

The browse page options are defined in the [`BrowseConfig` type](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-types.ts#L109). Read below for a breakdown of them.

#### Curated Tags

The Curated tags list is an array of tags to show in a separate section at the top of the browser page. It is an empty array by default.

#### Examples
Here is how you would add curated tags to the top of the Browse page:
```js
browse: {
  curatedTags: ['tag1', 'tag2', 'tag3'],
  //...
},
```

#### Hide Non-Clickable Badges
 The `BrowseConfig.hideNonClickableBadges` hides non-clickable badges in the homepage if `true`. By default is `false`.

#### Examples
This is how you turn it to true:
```js
browse: {
  hideNonClickableBadges: true,
  //...
},
```

#### Show All Tags

The `BrowseConfig.showAllTags` flag allows us to configure whether we should show all the tags or only the curated ones. The default is `true`.

#### Examples
This option shows all tags when true, or only curated tags if false:
```js
browse: {
  showAllTags: false,
  //...
},
```

#### Show Badges in homepage

By default, all available badges are shown on the homepage. The `browse.showBadgesInHome` configuration can be set to `false` to disable this. In addition, it is possible to hide the "non-clickable" badges using `browse.hideNonClickableBadges` configuration.

#### Examples
Here is how you would remove the badges list from the homepage
```js
browse: {
  //...
  showBadgesInHome: false,
},
```

## Column Lineage
This options allows you to configure column level lineage features in Amundsen.

It includes:
 * inAppListEnabled - whether the in-app column list lineage is enabled.
 * inAppPageEnabled - whether the in-app column lineage page is enabled.
 * urlGenerator - the lineage link for a given column

### Examples
Set these values to see column lineage:
```js
  columnLineage: {
    inAppListEnabled: true,
    inAppPageEnabled: true,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string,
      column: string
    ) => {
      // Some code here

      return `https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}&column=${column}`;
    }
  },
```

## Date

This config allows you to specify various date formats using [moment.js](https://momentjs.com/) across the app. There are three date formats in use shown below. These correspond to the `formatDate`, `formatDateTimeShort` and `formatDateTimeLong` utility functions, with the defaults shown below:

```js
date: {
  default: 'MMM DD, YYYY',
  dateTimeShort: 'MMM DD, YYYY ha z',
  dateTimeLong: 'MMMM Do YYYY [at] h:mm:ss a',
}
```

[Read here the reference](https://devhints.io/datetime#momentjs-format) for formatting.

### Examples
Set these values to get different formats:
```js
date: {
  default: 'YYYY-MM-DD',
  dateTimeShort: 'DD. MMM. YYYY hh:mm',
  dateTimeLong: 'DD. MMM. YYYY hh:mm:ss',
}
```

## Document Title
This configuration string specifies the root of the application title. By default this is 'Amundsen - Data Discovery Portal'.

### Examples
You can set this value with your company name:
```js
documentTitle: 'ACME - Amundsen - Data Discovery Portal',
```

## Editable Text

The [`EditableTextConfig`](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-types.ts#L465) configuration object allows us to configure the maximum length limits for editable fields.

With it, we configure the max length for table and column descriptions, with defaults being:
```js
editableText: {
  columnDescLength: 250,
  tableDescLength: 750,
},
```

### Examples
To change these values, simply update the character lengths:
```js
editableText: {
  columnDescLength: 100,
  tableDescLength: 500,
},
```

## Feature Lineage
This option allows you to configure the upstream lineage tab for features.

### Examples
Set this value to see feature lineage:
```js
  featureLineage: {
    inAppListEnabled: true,
  },
```

## Homepage Widgets
By default, a set of features are available on the homepage (e.g. the search bar, bookmarks). These can be customized in config-custom.ts by providing an alternate `homePageWidgets` value. The value is a list of `Widget` objects. Non-OSS widgets can be provided in the `widget.options.path` property, and props passed to widget components can be customized with the `widget.options.aditionalProps` property.

If a custom `homePageWidgets` config is provided, the default config will be ignored. So, for example, if you wanted to have all the default widgets plus a custom non-OSS widget component, you should copy all the homePageWidgets from [config-default.ts](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-default.ts) to your config-custom.ts, and then append your custom component. To omit one of the default widgets, you would copy the default list, and then delete the widget you didn't want.

### Examples
For example, if we wanted to place the Bookmarks widget at the top of the homepage, we could do:
```js
//...
homePageWidgets: {
    widgets: [
      {
        name: "MyBookmarksWidget",
        options: {
          path: "MyBookmarksWidget/index",
        },
      },
      {
        name: "SearchBarWidget",
        options: {
          path: "SearchBarWidget/index",
        },
      },
      {
        name: "BadgesWidget",
        options: {
          path: "BadgesWidget/index",
          additionalProps: {
            shortBadgesList: true,
          },
        },
      },
      {
        name: "TagsWidget",
        options: {
          path: "TagsWidget/index",
          additionalProps: {
            shortTagsList: true,
          },
        },
      },
    ],
  },
//...
```

## Indexing Optional Resources

In Amundsen, we currently support indexing other optional resources beyond tables.

### Index Users

Users themselves are data resources and user metadata helps to facilitate network based discovery. When users are indexed they will show up in search results, and selecting a user surfaces a profile page that displays that user's relationships with different data resources.

After ingesting user metadata into the search and metadata services, set `IndexUsersConfig.enabled` to `true` on the application configuration to display the UI for the aforementioned features.

### Index Dashboards

Introducing dashboards into Amundsen allows users to discovery data analysis that has been already done. When dashboards are indexed they will show up in search results, and selecting a dashboard surfaces a page where users can explore dashboard metadata.

After ingesting dashboard metadata into the search and metadata services, set `IndexDashboardsConfig.enabled` to `true` on the application configuration to display the UI for the aforementioned features.

### Index Features
When this configuration is enabled, ML features will be avaialable as searchable resources. This requires feature objects to be ingested via Databuilder and made available in the metadata and serch services.

### Examples
This enables this feature in the frontend only:
```js
//...
indexFeatures: {
  enabled: true,
},
//...
```

## Issue Tracking

In order to enable Issue Tracking, set `IssueTrackingConfig.enabled` to `true` to see UI features. Further configuration is required to fully enable the feature, please see this [entry](flask_config.md#issue-tracking-integration-features).

To prepopulate the issue description text field with a template to suggest more detailed information to be provided by the user when an issue is reported, set `IssueTrackingConfig.issueDescriptionTemplate` with the desired string.

A default project ID to specify where issues will be created is set in the flask configuration, but to allow users to override this value and choose which project their issue is created in, set `IssueTrackingConfig.projectSelection.enabled`
to `true`. This will add an extra input field in the `Report an issue` modal that will accept a Jira project key, but if no input is entered, it will use the value that is set in the flask configuration. This feature is currently only
implemented for use with Jira issue tracking.

- Set `IssueTrackingConfig.projectSelection.title` to add a title to the input field, for example `Jira project key (optional)`, to let users know what to enter in the text field.
- An optional config `IssueTrackingConfig.projectSelection.inputHint` can be set to show a hint in the input field, which can be helpful to show users an example that conveys the expected format of the project key.

### Examples
This is an example of configuration for issue tracking with JIRA:
```js
//...
issueTracking: {
  enabled: true,
  issueDescriptionTemplate:
    "Affected column(s): \nProducing DAG, if known: \nFurther details: \n",
  projectSelection: {
    enabled: true,
    title: "Jira project key (optional)",
    inputHint: "HELP",
  },
},
//...
```

## Custom Logo
We can configure the application to show a custom image on the logo instead of the default Amundsen logo. For that, you would:

1. Add your logo to the folder in `amundsen_application/static/images/`.
2. Set the the `logoPath` key on the to the location of your image.

### Examples
To add a custom logo, set this up:
```js
logoPath: "/static/images/custom-logo.svg",
```
So you would see something like this:
<img src='img/header-dark-custom-logo.png' width='50%' />

## Custom Title
We can also set a custom title for the application (the default is 'Amundsen'). For that, we would use the 'logoTitle' configuration.

### Examples
To add a custom title, set this up:
```js
logoTitle: "Your Custom App Name",
```

## Mail Client Features

Amundsen has two features that leverage the custom mail client -- the feedback tool and notifications.

As these are optional features, our `MailClientFeaturesConfig` can be used to hide/display any UI related to these features:

1. Set `MailClientFeaturesConfig.feedbackEnabled` to `true` in order to display the `Feedback` component in the UI.
2. Set `MailClientFeaturesConfig.notificationsEnabled` to `true` in order to display the optional UI for users to request more information about resources on the `TableDetail` page.

For information about how to configure a custom mail
client, please see this [entry](flask_config.md#mail-client-features) in our flask configuration doc.

## Navigation App Suite

This configuration allows to show a popover menu with related application links. This is hidden by default, and only will show up if you pass an array of links to it.

### Examples
Here is how you would set a list of links:
```js
//...
navAppSuite: [
  {
    label: 'App One',
    id: 'appOne',
    href: 'https://www.lyft.com',
    target: '_blank',
    iconPath: '/static/images/app-one-logo.svg',
  },
  {
    label: 'App Two',
    id: 'appTwo',
    href: 'https://www.amundsen.io/',
    iconPath: '/static/images/app-two-logo.svg',
  },
  //...
],
//...
```
Which would render as:
<img src='img/app-suite.png' width='50%' />

## Navigation Links
This configuration option allows you to customize the Navigation links at the top right side of the global header:

<img src='img/nav-links.png' width='50%' />

### Examples
Here is how you would set them in the configuration:
```js
//...
navLinks: [
    {
      href: "/announcements",
      id: "nav::announcements",
      label: "Announcements",
      use_router: true,
    },
    {
      href: "https://external.link.com",
      id: "nav::docs",
      label: "Docs",
      target: "_blank",
      use_router: false,
    },
  ],
//...
```
Note how we can add internal links (with 'use_router' true) or external links with 'target' set to _blank so they open on a new tab.

## Navigation Theme

This configuration allows users to select a navigation theme for the global header of the application. This is 'dark' by default:

<img src='img/header-dark-default-logo.png' width='50%' />


### Examples
Here is how you would set it to the 'light' theme:
```js
//...
navTheme: 'light',
//...
```

Which would render like the following:
<img src='img/header-light-default-logo.png' width='50%' />

## Nested Columns
Nested columns will be enabled in the frontend by default if complex column types are parsed and ingested using the [ComplexTypeTransformer](https://github.com/amundsen-io/amundsen/tree/main/databuilder#complextypetransformer).

To expand all nested column type rows by default if the total number of rows does not exceed a specific value, set `nestedColumns.maxNestedColumns` to the desired limit. The default value is set to 500 to avoid an unbounded expansion.

### Examples
Simply set the maximum nested columns allowed in the UI:
```js
//...
  nestedColumns: {
    maxNestedColumns: 1000,
  },
//...
```

## Number Format
This configuration allows us to format different types of numbers like currency, and percentages in the desired format. Internally, it applies the first argument for [Intl.NumberFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat), so you can check the options there.

### Examples
```js
//...
numberFormat: {
  numberSystem: 'jap-JP'
},
//...
```

## Product Tour

The Product Tour for Amundsen is a UI based walkthrough configurable component that helps onboard users into Amundsen. Alternatively, it helps us promote new features added to Amundsen, and educate our users about its use.

The Tour triggers in two different modes. The first is a page tour, like a general "Getting started with Amundsen" walkthough, while the second highlights different features. Both would be formed by an overlay and a modal that is attached to elements in the UI.

This modal window has a "Dimiss" button that would hide the Tour altogether; a "Back" button that would move the user to the previous tour step, a "Next" button that moves it forward and a "Close" button with the usual "X" shape in the top right corner.

For Amundsen maintainers, we extend the JavaScript configuration file with a block about the tour. This object has a shape like this when creating a "page tour":


### Examples
```js
...
productTour: {
  '/': [
    {
      isFeatureTour: false,
      isShownOnFirstVisit: true,
      isShownProgrammatically: true,
      steps: [
        {
          target: '.nav-bar-left a',
          title: 'Welcome to Amundsen',
          content:
            'Hi!, welcome to Amundsen, your data discovery and catalog product!',
          disableBeacon: true,
        },
        {
          target: '.search-bar-form .search-bar-input',
          title: 'Search for resources',
          content:
            'Here you will search for the resources you are looking for',
        },
        {
          target: '.bookmark-list-header',
          title: 'Save your bookmarks',
          content:
            'Here you will see a list of the resources you have bookmarked',
        },
      ],
    },
  ],
},
```

Where:

- The keys of the productTour object are the paths to the pages with a tour. They support simple wildcards `*`, only at the end (for example: `/table_detail/*`).
- `isFeatureTour` - tells if the tour is for a whole page (false) or just for one feature within the page.
- `isShownOnFirstVisit` - whether the users will see the tour on their first visit.
- `isShownProgrammatically` - whether we want to add the button to trigger the tour to the global navigation
- `steps` - a list of CSS selectors to point the tour highlight, a title of the step and the content (text only). `disableBeacon` controls whether if we show a purple beacon to guide the users to the initial step of the tour.

For "feature tours", the setup would be similar, but `isFeatureTour` would be true, and `disableBeacon` should be false (the default), so that users can start the tour.


## Resource Configurations

This configuration drives resource specific aspects of the application's user interface. Each supported resource should be mapped to an object that matches or extends the `BaseResourceConfig`.

### Base Configuration

All resource configurations must match or extend the `BaseResourceConfig`. This configuration supports the following options:

1. `displayName`: The name displayed throughout the application to refer to this resource type.
2. `filterCategories`: An optional `FilterConfig` object. When set for a given resource, that resource will display filter options in the search page UI.
3. `supportedSources`: An optional `SourcesConfig` object.

#### Filter Categories

The `FilterConfig` is an array of objects that match any of the supported filter options. We currently support a `CheckboxFilterCategory`, `InputFilterCategory` and a `ToggleFilterCategory`. See our [config-types](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-types.ts) for more information about each option.

#### Supported Sources

The `SourcesConfig` can be used for the customizations detailed below. See examples in [config-default.ts](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-default.ts).

##### Custom Icons

You can configure custom icons to be used throughout the UI when representing entities from particular sources. On the `supportedSources` object, add an entry with the `id` used to reference that source and map to an object that specifies the `iconClass` for that database. This `iconClass` should be defined in [icons.scss](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/css/_icons.scss).

##### Display Names

You can configure a specific display name to be used throughout the UI when representing entities from particular sources. On the `supportedSources` object, add an entry with the `id` used to reference that source and map to an object that specified the `displayName` for that source.

### Table Configuration

To configure Table related features we have created a new resource configuration `TableResourceConfig` which extends `BaseResourceConfig`. In addition to the configurations explained above it also supports `supportedDescriptionSources`.

#### Supported Description Sources

A table resource may have a source of table and column description attached to it. We can customize it by using `supportedDescriptionSources` object which is an optional object.
This object has `displayName` and `iconPath`, which can be used throughout the UI to represent a particular description source. See example in [config-default.ts](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/js/config/config-default.ts).
For configuring new description sources, add an entry in `supportedDescriptionSources` with the `id` used to reference that source and add desired display name and icon for it.

## Table Stats

If you have a stat field that is made of a JSON like set of value names and counts, you can show that as a set of "unique values". You can see an example of this in the following figure:

<img src='img/distinct_values.png' width='50%' />

To achieve this, you will need to modify your custom configuration (config-custom.ts) by adding the name of the stat_type field that holds these values. You can find the config property in the stats section for table resource:

```js
[ResourceType.table]: {
  //...
  stats: {
    uniqueValueTypeName: "keyNameExample",
  },
}
```

The unique values set needs to be an object like this:

```json
    {
      end_epoch: 1609522182,
      start_epoch: 1608917382,
      stat_type: 'keyNameExample',
      stat_val:
        "{'Category': 66, 'AnotherCategory': 54, 'More': 48}",
    },
```

## Notices

We now can add notices to tables and dashboards. These notices allows Amundsen administrators to show informational, warning and alert messages related to the different resources (tables, dashboards, eventually people) we expose in Amundsen.

This feature help administrators show messages related to deprecation, updates (or lack of), and informational messages related to specific resources.

A notice is a small box with an icon and a message containing HTML markup (like links and bolded text). These will come in three flavors:

<figure>
  <figcaption>Informational: Marked with a blue "i" icon on the right side</figcaption>
  <img src='img/notices-info-table.png' width='50%' />
</figure>

<figure>
  <figcaption>Warning: Marked with an orange exclamation mark icon on the right side</figcaption>
  <img src='img/notices-warning-table.png' width='50%' />
</figure>

<figure>
  <figcaption>Alert: Marked with a red exclamation mark icon on the right side</figcaption>
  <img src='img/notices-alert-table.png' width='50%' />
</figure>

To set them up, we'll use the current configuration objects for the resources. In the event that we want to add the same notice to every table that follows a particular pattern, we use a wildcard character, \*, for pattern matching. In addition, we can have dynamic HTML messages to allow for notices to change their message based on what table it is.

For example, if company X wants to deprecate the use of one table or dashboard, they can opt to add new notices in their configuration file:

```js
  resourceConfig: {
    [ResourceType.table]: {
      ... //Table Resource Configuration
      notices: {
          "<CLUSTER>.<DATABASE>.<SCHEMA>.<TABLENAME>": {
            severity: NoticeSeverity.ALERT,
            messageHtml: `This table is deprecated, please use <a href="<LINKTONEWTABLEDETAILPAGE>">this new table</a> instead.`,
          },
      },
    },
    [ResourceType.dashboard]: {
      ... //Dashboard Resource Configuration
      notices: {
          "<PRODUCT>.<CLUSTER>.<GROUPNAME>.<DASHBOARDNAME>": {
            severity: NoticeSeverity.WARNING,
            messageHtml: `This dashboard is deprecated, please use <a href="<LINKTONEWDASHBOARDDETAILPAGE>">this new dashboard</a> instead.`,
          },
      },
    },

  },
```

The above code will show a notice with a red exclamation icon whenever a final user visits the table's Table Detail page or the Dashboard Detail page.

If you want to target several tables at once, you can use wildcards as shown below:

```js
  resourceConfig: {
    [ResourceType.table]: {
      ... //Table Resource Configuration
      notices: {
          "<CLUSTER>.<DATABASE>.<SCHEMA>.*": {
            severity: NoticeSeverity.ALERT,
            messageHtml: `This table is deprecated`,
          },
      },
    },
    [ResourceType.dashboard]: {
      ... //Dashboard Resource Configuration
      notices: {
          "<PRODUCT>.<CLUSTER>.<GROUPNAME>.*": {
            severity: NoticeSeverity.WARNING,
            messageHtml: `This dashboard is deprecated`,
          },
      },
    },

  },
```

The above code will show a notice with a red exclamation icon whenever a final user visits any table within the specified cluster, database, and schema or any dashboard within the specified product, cluster, and groupname.

Wildcards can also replace individual parts of table names. If you want to add a notice to all resources whose names followed the pattern foo\_\*:

```js
  resourceConfig: {
    [ResourceType.table]: {
      ... //Table Resource Configuration
      notices: {
          "<CLUSTER>.<DATABASE>.<SCHEMA>.foo_*": {
            severity: NoticeSeverity.INFO,
            messageHtml: `This table has information`,
          },
      },
    },
    [ResourceType.dashboard]: {
      ... //Dashboard Resource Configuration
      notices: {
          "<PRODUCT>.<CLUSTER>.<GROUPNAME>.foo_*": {
            severity: NoticeSeverity.INFO,
            messageHtml: `This dashboard has information`,
          },
      },
    },

  },
```

The above code will show the message on any table with the specified cluster, database and schema whose table name starts with `foo_` or any dashboard with the specified product, cluster, and groupname whose dashboard name starts with `foo_`.

If you want to use a dynamic HTML message that changes depending on the name of the resource, you can use string formatting as shown below:

```js
  resourceConfig: {
    [ResourceType.table]: {
      ... //Table Resource Configuration
      notices: {
          "<CLUSTER>.<DATABASE>.<SCHEMA>.*": {
            severity: NoticeSeverity.ALERT,
            messageHtml: (resourceName) => {
              const [cluster, datasource, schema, table] = resourceName.split('.');
              return `This schema is deprecated, please use <a href="https://amundsen.<company>.net/table_detail/${cluster}/${datasource}/SCHEMA/${table}">this table instead</a>`;
            },
          },
      },
    },
    [ResourceType.dashboard]: {
      ... //Dashboard Resource Configuration
      notices: {
          "<PRODUCT>.<CLUSTER>.<GROUPNAME>.*": {
            severity: NoticeSeverity.WARNING,
            messageHtml: (resourceName) => {
              const [product, cluster, groupname, dashboard] = resourceName.split('.');
              return `${groupname} is deprecated, please use <a href="LINKTODASHBOARD">this dashboard instead</a>`;
            },
          },
      },
    },

  },
```

The above code will show a notice with a dynamic message and a red exclamation icon whenever a final user visits any table within the specified cluster, database, and schema or any dashboard within the specified product, cluster, and groupname. We can also use dynamic messages for notices without the wildcard by replacing the \* with the specific table or dashboard name.

You can also add extra information on the notices, that will be rendered as a modal. Here is a configuration example:
```js
  resourceConfig: {
    [ResourceType.table]: {
      ... //Table Resource Configuration
      notices: {
          "<CLUSTER>.<DATABASE>.<SCHEMA>.<TABLENAME>": {
            severity: NoticeSeverity.ALERT,
            messageHtml: `This table is deprecated, please use <a href="<LINKTONEWTABLEDETAILPAGE>">this new table</a> instead.`,
            payload: {
              testKey: "testValue",
              testKey2: 'testHTMLVAlue <a href="http://lyft.com">Lyft</a>',
            },
          },
      },
    },

  },
```

The above code will show a notice with a "See details" link that will open a modal that renders a list of the payload key/value pairs.


This feature's ultimate goal is to allow Amundsen administrators to point their users to more trusted/higher quality resources without removing the old references.

Learn more about the future developments for this feature in [its RFC](https://github.com/amundsen-io/rfcs/blob/master/rfcs/029-resource-notices.md).


### Dynamic Notices
We are now going to allow for fetching dynamically the notices related to different resources like tables, dashboards, users, and features.

For that, you will first enabled the `hasDynamicNoticesEnabled` flag inside the `resourceConfig` object of the goal resource. This flag is optional and will default to `false` if not set.

#### Examples
Example of this option enabled on tables and dashboards:
```ts
  resourceConfig: {
    [ResourceType.table]: {
      ... //Table Resource Configuration
      hasDynamicNoticesEnabled: true,
    },
    [ResourceType.dashboard]: {
      ... //Dashboard Resource Configuration
      hasDynamicNoticesEnabled: true,
    },
  },
```

## Search Pagination
With this configuration option you can choose how many results you want to show on your search page for any given search query. The default is 10 results.

### Examples
Simply pass down a number:
```js
//...
searchPagination: {
    resultsPerPage: 20,
},
//...
```

## Table Lineage
 This option allows you to customize the "Table Lineage" links of the "Table Details" page. Note that this feature is intended to link to an **external lineage provider**.

 It includes these options
 * iconPath - Path to an icon image to display next to the lineage URL.
 * isBeta - Adds a "beta" tag to the section header.
 * isEnabled - Whether to show or hide this section
 * urlGenerator - Generate a URL to the third party lineage website
 * inAppListEnabled - Enable the in app Upstream/Downstream tabs for table lineage. Requires backend support.
 * inAppListMessages - when an in app list is enabled this will add a custom message at the end of the lineage tabs content.
 * disableAppListLinks - Set up table field based regular expression rules to disable lineage list view links.

### Examples
Here is an example configuration for an external provider:
```js
//...
  tableLineage: {
    externalEnabled: true,
    iconPath: '/static/images/ICON.png',
    isBeta: true,
    defaultLineageDepth: 5,
    inAppListEnabled: true,
    inAppPageEnabled: false,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string
    ) => {
      // Some logic here to calculate the URL

      return encodeURI(`https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`);
    }
  },
//...
```

## Table Profile
This configuration allows you to customize the "Table Profile" section of the "Table Details" page.

The options are:
* isBeta - Adds a "beta" tag to the "Table Profile" section header.
* isExploreEnabled - Enables the third party SQL exploration application.
* exploreUrlGenerator - Generates a URL to a third party SQL explorable website.

### Examples
Here is an example for an SQL exploration tool:
```js
//...
  tableProfile: {
    isBeta: true,
    isExploreEnabled: true,
    exploreUrlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string,
      partitionKey?: string,
      partitionValue?: string
    ) => {
      // Some logic here

      return `https://DEFAULT_EXPLORE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`;
    }
  },
//...
```

## Table Quality Checks
This configuration allows you to query and display data quality check status from an external provider. The API must be configured. Default is false.

### Examples
Simply enable it:
```js
//...
  tableQualityChecks: {
    isEnabled: true,
  },
//...
```

## User Id label
This is a temporary configuration due to lacking string customization/translation support. It will show as `Please enter <userIdLabel>`. Default is 'email address'.

### Examples
Simply add your string:
```js
//...
  userIdLabel: 'email',
//...
```
