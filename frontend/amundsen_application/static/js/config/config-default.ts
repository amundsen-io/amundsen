import { AppConfig } from './config-types';

const configDefault: AppConfig = {
  badges: {},
  browse: {
    curatedTags: [],
    showAllTags: true,
  },
  editableText: {
    tableDescLength: 750,
    columnDescLength: 250,
  },
  google: {
    enabled: false,
    key: 'default-key',
    sampleRate: 100,
  },
  indexUsers: {
    enabled: false,
  },
  logoPath: null,
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  navLinks: [
    {
      label: "Announcements",
      id: "nav::announcements",
      href: "/announcements",
      use_router: true,
    },
    {
      label: "Browse",
      id: "nav::browse",
      href: "/browse",
      use_router: true,
    }
  ],
  resourceConfig: {
    datasets: {
      'bigquery': {
        displayName: 'BigQuery',
        iconClass: 'icon-bigquery',
      },
      'hive': {
        displayName: 'Hive',
        iconClass: 'icon-hive',
      },
      'presto': {
        displayName: 'Presto',
        iconClass: 'icon-presto',
      },
      'postgres': {
        displayName: 'Postgres',
        iconClass: 'icon-postgres',
      },
      'redshift': {
        displayName: 'Redshift',
        iconClass: 'icon-redshift',
      },
    },
  },
  tableLineage: {
    iconPath: 'PATH_TO_ICON',
    isBeta: false,
    isEnabled: false,
    urlGenerator: (database: string, cluster: string, schema: string, table: string) => {
      return `https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`;
    },
  },
  tableProfile: {
    isBeta: false,
    isExploreEnabled: false,
    exploreUrlGenerator: (database: string, cluster: string, schema: string, table: string, partitionKey?: string, partitionValue?: string) => {
      return `https://DEFAULT_EXPLORE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`;
    }
  },
};

export default configDefault;
