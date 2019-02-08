/**
 * AppConfig and AppConfigCustom should share the same definition, except each field in AppConfigCustom
 * is optional. If you choose to override one of the configs, you must provide the full type definition
 * for that section.
 */

export interface AppConfig {
  browse: BrowseConfig;
  exploreSql: ExploreSqlConfig;
  google: GoogleAnalyticsConfig;
  lineage: LineageConfig;
  navLinks: Array<LinkConfig>;
}

export interface AppConfigCustom {
  browse?: BrowseConfig;
  exploreSql?: ExploreSqlConfig;
  google?: GoogleAnalyticsConfig
  lineage?: LineageConfig;
  navLinks?: Array<LinkConfig>;
}

/**
 * GoogleAnalyticsConfig - Customize 'gtag' - Google Tag Manager.
 *
 * Key - The unique analytics key for your site
 * Sample Rate - The percentage of users (0 - 100) to track site speed.
 */
interface GoogleAnalyticsConfig {
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
 * ExploreSqlCongfig - Customize an optional section in the 'table details' page where users can run SQL queries.
 *
 * enabled - Whether to show or hide this section
 * generateUrl - Generates a URL to a third party SQL explorable website.
 */
interface ExploreSqlConfig {
  enabled: boolean;
  generateUrl: (database: string, cluster: string, schema: string, table: string, partitionKey?: string, partitionValue?: string) => string;
}

/**
 * LineageConfig - Customize an optional section in the 'table details' page where users can see a table's lineage.
 *
 * enabled - Whether to show or hide this section
 * generateUrl - Generate a URL to the third party lineage website
 * iconPath - Path to an icon image to display next to the lineage URL.
 */
interface LineageConfig {
  enabled: boolean;
  generateUrl: (database: string, cluster: string, schema: string , table: string) => string;
  iconPath: string;
}

interface LinkConfig {
  href: string;
  label: string;
  target?: string;
  use_router: boolean;
}
