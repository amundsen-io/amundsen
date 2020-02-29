import { AppConfig } from './config-types';

import { FilterType, ResourceType } from '../interfaces';

const configDefault: AppConfig = {
  badges: {},
  browse: {
    curatedTags: [],
    showAllTags: true,
  },
  date: {
    default: 'MMM DD, YYYY',
    dateTimeShort: 'MMM DD, YYYY ha z',
    dateTimeLong: 'MMMM Do YYYY [at] h:mm:ss a',
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
  issueTracking: {
    enabled: false
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
    [ResourceType.table]: {
      displayName: 'Datasets',
      supportedDatabases: {
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
      filterCategories: [
        {
          categoryId: 'database',
          displayName: 'Source',
          helpText: 'Enter exact database name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'column',
          displayName: 'Column',
          helpText: 'Enter exact column name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'schema',
          displayName: 'Schema',
          helpText: 'Enter exact schema name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'table',
          displayName: 'Table',
          helpText: 'Enter exact table name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'tag',
          displayName: 'Tag',
          helpText: 'Enter exact tag name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
      ]
    },
    [ResourceType.user]: {
      displayName: 'People'
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
