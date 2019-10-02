/**
 * AppConfig and AppConfigCustom should share the same definition, except each field in AppConfigCustom
 * is optional. If you choose to override one of the configs, you must provide the full type definition
 * for that section.
 */

export interface AppConfig {
  browse: BrowseConfig;
  editableText: EditableTextConfig;
  google: GoogleAnalyticsConfig;
  indexUsers: IndexUsersConfig;
  logoPath: string | null;
  mailClientFeatures: MailClientFeaturesConfig;
  navLinks: Array<LinkConfig>;
  tableLineage: TableLineageConfig;
  tableProfile: TableProfileConfig;
}

export interface AppConfigCustom {
  browse?: BrowseConfig;
  editableText?: EditableTextConfig;
  google?: GoogleAnalyticsConfig
  indexUsers?: IndexUsersConfig;
  logoPath?: string;
  mailClientFeatures: MailClientFeaturesConfig;
  navLinks?: Array<LinkConfig>;
  tableLineage?: TableLineageConfig;
  tableProfile?: TableProfileConfig;
}

/**
 * GoogleAnalyticsConfig - Customize 'gtag' - Google Tag Manager.
 *
 * Key - The unique analytics key for your site
 * Sample Rate - The percentage of users (0 - 100) to track site speed.
 */
interface GoogleAnalyticsConfig {
  enabled: boolean;
  key: string;
  sampleRate: number;
}

/**
 * BrowseConfig - Customize the 'browse' page.
 *
 * curatedTags - An array of tags to show in a separate section at the top.
 * showAllTags - Shows all tags when true, or only curated tags if false
 */
interface BrowseConfig {
  curatedTags: Array<string>;
  showAllTags: boolean;
}

/**
 * MailClientFeaturesConfig - Enable/disable UI features with a dependency on
 *                            configuring a custom mail client.
 *
 * feedbackEnabled - Enables the feedback feature UI
 * notificationsEnabled - Enables any UI related to sending notifications to users
 */
interface MailClientFeaturesConfig {
  feedbackEnabled: boolean;
  notificationsEnabled: boolean;
}

/**
 * TableProfileConfig - Customize the "Table Profile" section of the "Table Details" page.
 *
 * isBeta - Adds a "beta" tag to the "Table Profile" section header.
 * isExploreEnabled - Enables the third party SQL explore feature.
 * exploreUrlGenerator - Generates a URL to a third party SQL explorable website.
 */
interface TableProfileConfig {
  isBeta: boolean;
  isExploreEnabled: boolean;
  exploreUrlGenerator: (database: string, cluster: string, schema: string, table: string, partitionKey?: string, partitionValue?: string) => string;
}

/**
 * TableLineageConfig - Customize the "Table Lineage" section of the "Table Details" page.
 *
 * iconPath - Path to an icon image to display next to the lineage URL.
 * isBeta - Adds a "beta" tag to the section header.
 * isEnabled - Whether to show or hide this section
 * urlGenerator - Generate a URL to the third party lineage website
 */
interface TableLineageConfig {
  iconPath: string;
  isBeta: boolean;
  isEnabled: boolean;
  urlGenerator: (database: string, cluster: string, schema: string , table: string) => string;
}

export interface LinkConfig {
  href: string;
  id: string;
  label: string;
  target?: string;
  use_router: boolean;
}

/**
 * IndexUsersConfig - When enabled, the IndexUsers feature will index users as searchable resources. This requires
 * user objects are ingested via Databuilder
 *
 * enabled - Enables/disables this feature in the frontend only
 */
interface IndexUsersConfig {
  enabled: boolean;
}

/**
 * EditableTextConfig - Configure max length limits for editable fields
 *
 * tableDescLength - maxlength for table descriptions
 * columnDescLength - maxlength for column descriptions
 */
interface EditableTextConfig {
  tableDescLength: number;
  columnDescLength: number;
}
