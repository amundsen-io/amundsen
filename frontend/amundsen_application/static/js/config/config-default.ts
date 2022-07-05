import { FilterType, ResourceType, SortDirection } from '../interfaces';
import { AppConfig } from './config-types';

const configDefault: AppConfig = {
  badges: {},
  browse: {
    curatedTags: [],
    showAllTags: true,
    showBadgesInHome: true,
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
  analytics: {
    plugins: [],
  },
  indexDashboards: {
    enabled: false,
  },
  indexUsers: {
    enabled: false,
  },
  indexFeatures: {
    enabled: false,
  },
  userIdLabel: 'email address',
  issueTracking: {
    enabled: false,
    issueDescriptionTemplate: '',
    projectSelection: {
      enabled: false,
      title: 'Issue project key (optional)',
      inputHint: '',
    },
  },
  logoPath: null,
  logoTitle: 'AMUNDSEN',
  documentTitle: 'Amundsen - Data Discovery Portal',
  numberFormat: null,
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  announcements: {
    enabled: false,
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
        superset: {
          displayName: 'Superset',
          iconClass: 'icon-superset',
        },
        databricks_sql: {
          displayName: 'Databricks SQL',
          iconClass: 'icon-databricks-sql',
        },
      },
      filterCategories: [
        {
          categoryId: 'product',
          displayName: 'Product',
          helpText:
            'Enter one or more comma separated values with exact product names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'group_name',
          displayName: 'Group',
          helpText:
            'Enter one or more comma separated values with exact group names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'name',
          displayName: 'Name',
          helpText:
            'Enter one or more comma separated values with exact dashboard names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'tag',
          displayName: 'Tag',
          helpText:
            'Enter one or more comma separated values with exact tag names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
      ],
      notices: {},
      searchHighlight: {
        enableHighlight: true,
      },
    },
    [ResourceType.feature]: {
      displayName: 'ML Features',
      supportedSources: {
        bigquery: {
          displayName: 'BigQuery',
          iconClass: 'icon-bigquery',
        },
        delta: {
          displayName: 'Delta',
          iconClass: 'icon-delta',
        },
        dremio: {
          displayName: 'Dremio',
          iconClass: 'icon-dremio',
        },
        druid: {
          displayName: 'Druid',
          iconClass: 'icon-druid',
        },
        hive: {
          displayName: 'Hive',
          iconClass: 'icon-hive',
        },
        oracle: {
          displayName: 'Oracle',
          iconClass: 'icon-oracle',
        },
        presto: {
          displayName: 'Presto',
          iconClass: 'icon-presto',
        },
        trino: {
          displayName: 'Trino',
          iconClass: 'icon-trino',
        },
        postgres: {
          displayName: 'Postgres',
          iconClass: 'icon-postgres',
        },
        redshift: {
          displayName: 'Redshift',
          iconClass: 'icon-redshift',
        },
        snowflake: {
          displayName: 'Snowflake',
          iconClass: 'icon-snowflake',
        },
      },
    },
    [ResourceType.table]: {
      displayName: 'Datasets',
      supportedSources: {
        bigquery: {
          displayName: 'BigQuery',
          iconClass: 'icon-bigquery',
        },
        delta: {
          displayName: 'Delta',
          iconClass: 'icon-delta',
        },
        dremio: {
          displayName: 'Dremio',
          iconClass: 'icon-dremio',
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
        trino: {
          displayName: 'Trino',
          iconClass: 'icon-trino',
        },
        postgres: {
          displayName: 'Postgres',
          iconClass: 'icon-postgres',
        },
        redshift: {
          displayName: 'Redshift',
          iconClass: 'icon-redshift',
        },
        snowflake: {
          displayName: 'Snowflake',
          iconClass: 'icon-snowflake',
        },
        elasticsearch: {
          displayName: 'Elasticsearch',
          iconClass: 'icon-elasticsearch',
        },
        teradata: {
          displayName: 'Teradata',
          iconClass: 'icon-teradata',
        },
      },
      filterCategories: [
        {
          categoryId: 'database',
          displayName: 'Source',
          helpText:
            'Enter one or more comma separated values with exact database names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'column',
          displayName: 'Column',
          helpText:
            'Enter one or more comma separated values with exact column names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'schema',
          displayName: 'Schema',
          helpText:
            'Enter one or more comma separated values with exact schema names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'table',
          displayName: 'Table',
          helpText:
            'Enter one or more comma separated values with exact table names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'tag',
          displayName: 'Tag',
          helpText:
            'Enter one or more comma separated values with exact tag names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
      ],
      sortCriterias: {
        sort_order: {
          name: 'Table Default',
          key: 'sort_order',
          direction: SortDirection.ascending,
        },
        name: {
          name: 'Alphabetical',
          key: 'name',
          direction: SortDirection.descending,
        },
      },
      supportedDescriptionSources: {
        dremio: {
          displayName: 'Dremio',
          iconPath: '/static/images/icons/logo-dremio.svg',
        },
        github: {
          displayName: 'Github',
          iconPath: '/static/images/github.png',
        },
      },
      notices: {},
      searchHighlight: {
        enableHighlight: true,
      },
    },
    [ResourceType.feature]: {
      displayName: 'ML Features',
      supportedSources: {
        hive: {
          displayName: 'Hive',
          iconClass: 'icon-hive',
        },
      },
      filterCategories: [
        {
          categoryId: 'entity',
          displayName: 'Entity',
          helpText:
            'Enter one or more comma separated values with exact entity names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'name',
          displayName: 'Feature Name',
          helpText:
            'Enter one or more comma separated values with exact feature names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'group',
          displayName: 'Feature Group',
          helpText:
            'Enter one or more comma separated values with exact feature group names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
        {
          categoryId: 'tag',
          displayName: 'Tag',
          helpText:
            'Enter one or more comma separated values with exact tag names or regex wildcard patterns',
          type: FilterType.INPUT_SELECT,
        },
      ],
      notices: {},
      searchHighlight: {
        enableHighlight: true,
      },
    },
    [ResourceType.user]: {
      displayName: 'People',
      searchHighlight: {
        enableHighlight: false,
      },
    },
  },
  featureLineage: {
    inAppListEnabled: false,
  },
  tableLineage: {
    inAppListEnabled: false,
    inAppPageEnabled: false,
    externalEnabled: false,
    iconPath: 'PATH_TO_ICON',
    isBeta: false,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string
    ) =>
      `https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`,
  },
  columnLineage: {
    inAppListEnabled: false,
    inAppPageEnabled: false,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string,
      column: string
    ) =>
      `https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}&column=${column}`,
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
    ) =>
      `https://DEFAULT_EXPLORE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`,
  },
  tableQualityChecks: {
    isEnabled: false,
  },
  nestedColumns: {
    maxNestedColumns: 500,
  },
  productTour: {},
  searchPagination: {
    resultsPerPage: 10,
  },
};

export default configDefault;
