/**
 * AppConfig and AppConfigCustom should share the same definition, except each field in AppConfigCustom
 * is optional. If you choose to override one of the configs, you must provide the full type definition
 * for that section.
 */

export interface AppConfig {
  browse: BrowseConfig;
  exploreSql: ExploreSqlConfig;
  google: GoogleAnalyticsConfig;
  navLinks: Array<LinkConfig>;
}

export interface AppConfigCustom {
  google?: GoogleAnalyticsConfig
  browse?: BrowseConfig;
  exploreSql?: ExploreSqlConfig;
  navLinks?: Array<LinkConfig>;
}

interface GoogleAnalyticsConfig {
  key: string;
  sampleRate: number;
}

interface BrowseConfig {
  curatedTags: Array<string>;
  showAllTags: boolean;
}

interface ExploreSqlConfig {
  enabled: boolean;
  generateUrl: (database: string, cluster: string, schema: string, table: string, partitionKey?: string, partitionValue?: string) => string;
}

interface LinkConfig {
  href: string;
  label: string;
  target?: string;
  use_router: boolean;
}
