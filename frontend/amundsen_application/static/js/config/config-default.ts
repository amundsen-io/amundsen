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
  indexDashboards: {
    enabled: false,
  },
  indexUsers: {
    enabled: false,
  },
  userIdLabel: 'email address',
  issueTracking: {
    enabled: false,
  },
  logoPath: null,
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  announcements: {
    enabled: true,
  },
  navLinks: [
    {
      label: 'Announcements',
      id: 'nav::announcements',
      href: '/announcements',
      use_router: true,
    },
    {
      label: 'Browse',
      id: 'nav::browse',
      href: '/browse',
      use_router: true,
    },
  ],
  resourceConfig: {
    [ResourceType.dashboard]: {
      displayName: 'Dashboards',
      supportedSources: {
        mode: {
          displayName: 'Mode',
          iconClass: 'icon-mode',
        },
        redash: {
          displayName: 'Redash',
          iconClass: 'icon-redash',
        },
        tableau: {
          displayName: 'Tableau',
          iconClass: 'icon-tableau',
        },
      },
      filterCategories: [
        {
          categoryId: 'product',
          displayName: 'Product',
          helpText: 'Enter exact product name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'group_name',
          displayName: 'Groups',
          helpText: 'Enter exact group name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'name',
          displayName: 'Name',
          helpText: 'Enter exact dashboard name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'tag',
          displayName: 'Tag',
          helpText: 'Enter exact tag name or a regex wildcard pattern',
          type: FilterType.INPUT_SELECT,
        },
      ],
    },
    [ResourceType.table]: {
      displayName: 'Datasets',
      supportedSources: {
        bigquery: {
          displayName: 'BigQuery',
          iconClass: 'icon-bigquery',
        },
        druid: {
          displayName: 'Druid',
          iconClass: 'icon-druid',
        },
        hive: {
          displayName: 'Hive',
          iconClass: 'icon-hive',
        },
        presto: {
          displayName: 'Presto',
          iconClass: 'icon-presto',
        },
        postgres: {
          displayName: 'Postgres',
          iconClass: 'icon-postgres',
        },
        redshift: {
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
      ],
      supportedDescriptionSources: {
        github: {
          displayName: 'Github',
          iconPath: '/static/images/github.png',
        },
      },
    },
    [ResourceType.user]: {
      displayName: 'People',
    },
  },
  tableLineage: {
    iconPath: 'PATH_TO_ICON',
    isBeta: false,
    isEnabled: false,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string
    ) => {
      return `https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`;
    },
  },
  tableProfile: {
    isBeta: false,
    isExploreEnabled: false,
    exploreUrlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string,
      partitionKey?: string,
      partitionValue?: string
    ) => {
      return `https://DEFAULT_EXPLORE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`;
    },
  },
};

export default configDefault;
