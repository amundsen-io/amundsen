/* eslint-disable @typescript-eslint/no-unused-vars */
import { FilterType, ResourceType, SortDirection } from '../interfaces';
import { AppConfig, BadgeStyle } from './config-types';

const configDefault: AppConfig = {
  navAppSuite: null,
  navTheme: 'dark',
  nestedColumns: {
    maxNestedColumns: 500,
  },
  productTour: {},
  badges: {
    marts: {
      style: BadgeStyle.MARTS,
      displayName: 'Marts',
    },
    wrangling: {
      style: BadgeStyle.WRANGLING,
      displayName: 'Wrangling',
    },
    staging: {
      style: BadgeStyle.STAGING,
      displayName: 'Staging',
    },
    landing: {
      style: BadgeStyle.LANDING,
      displayName: 'Landing',
    },
    snowflake: {
      style: BadgeStyle.SNOWFLAKE,
      displayName: 'Snowflake',
    },
    mysql: {
      style: BadgeStyle.MYSQL,
      displayName: 'MySQL',
    },
    mssql: {
      style: BadgeStyle.MSSQL,
      displayName: 'MSSQL',
    },
    dbt: {
      style: BadgeStyle.DBT,
      displayName: 'dbt',
    },
    watermark: {
      style: BadgeStyle.WATERMARK,
      displayName: 'Watermark',
    },
    crediq: {
      style: BadgeStyle.CREDIQ,
      displayName: 'Cred iQ',
    },
    crefc: {
      style: BadgeStyle.CREFC,
      displayName: 'CREFC',
    },
  },
  browse: {
    curatedTags: [],
    showAllTags: true,
    showBadgesInHome: true,
    hideNonClickableBadges: false,
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
  // date: {
  //   dateTimeLong: 'MMMM Do YYYY [at] h:mm:ss a',
  //   dateTimeShort: 'MMM DD, YYYY ha z',
  //   default: 'MMM DD, YYYY',
  // },
  featureLineage: {
    inAppListEnabled: false,
  },
  homePageWidgets: {
    widgets: [
      {
        name: 'SearchBarWidget',
        options: {
          path: 'SearchBarWidget/index',
        },
      },
      {
        name: 'BadgesWidget',
        options: {
          additionalProps: {
            shortBadgesList: true,
          },
          path: 'BadgesWidget/index',
        },
      },
      {
        name: 'TagsWidget',
        options: {
          additionalProps: {
            shortTagsList: true,
          },
          path: 'TagsWidget/index',
        },
      },
      {
        name: 'MyBookmarksWidget',
        options: {
          path: 'MyBookmarksWidget/index',
        },
      },
      {
        name: 'PopularResourcesWidget',
        options: {
          path: 'PopularResourcesWidget/index',
        },
      },
    ],
  },
  indexDashboards: {
    enabled: false,
  },
  indexFeatures: {
    enabled: false,
  },
  indexUsers: {
    enabled: false,
  },
  indexFiles: {
    enabled: false,
  },
  indexProviders: {
    enabled: false,
  },
  issueTracking: {
    enabled: false,
    issueDescriptionTemplate: '',
    projectSelection: {
      enabled: false,
      inputHint: '',
      title: 'Issue project key (optional)',
    },
  },
  logoPath: null,
  logoTitle: 'Amundsen',
  documentTitle: 'Amundsen - Data Discovery Portal',
  footerContentHtml: 'Amundsen - Data Discovery Portal',
  numberFormat: null,
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  announcements: {
    enabled: false,
  },
  preview: {
    enabled: true,
    export: {
      enabled: true
    }
  },
  ai: {
    enabled: false
  },
  snowflake: {
    enabled: false,
    shares: {
      enabled: false
    }
  },
  bookmarks: {
    enabled: true,
  },
  navLinks: [
    {
      href: '/announcements',
      id: 'nav::announcements',
      label: 'Announcements',
      use_router: true,
    },
    {
      href: '/browse',
      id: 'nav::browse',
      label: 'Browse',
      use_router: true,
    },
  ],
  resourceConfig: {
    [ResourceType.dashboard]: {
      displayName: 'Canvases',
      supportedSources: {
        mode: {
          displayName: 'Mode',
          iconClass: 'icon-mode',
        },
        redash: {
          displayName: 'Redash',
          iconClass: 'icon-redash',
        },
        count: {
          displayName: 'Count',
          iconClass: 'icon-count',
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
        postgres: {
          displayName: 'Postgres',
          iconClass: 'icon-postgres',
        },
        presto: {
          displayName: 'Presto',
          iconClass: 'icon-presto',
        },
        redshift: {
          displayName: 'Redshift',
          iconClass: 'icon-redshift',
        },
        snowflake: {
          displayName: 'Snowflake',
          iconClass: 'icon-snowflake',
        },
        mysql: {
          displayName: 'MySQL',
          iconClass: 'icon-mysql',
        },
        mssql: {
          displayName: 'MSSQL',
          iconClass: 'icon-mssql',
        },
        clickhouse: {
          displayName: 'ClickHouse',
          iconClass: 'icon-clickhouse',
        },
        trino: {
          displayName: 'Trino',
          iconClass: 'icon-trino',
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
        mysql: {
          displayName: 'MySQL',
          iconClass: 'icon-mysql',
        },
        mssql: {
          displayName: 'MSSQL',
          iconClass: 'icon-mssql',
        },
        clickhouse: {
          displayName: 'ClickHouse',
          iconClass: 'icon-clickhouse',
        },
        elasticsearch: {
          displayName: 'Elasticsearch',
          iconClass: 'icon-elasticsearch',
        },
        teradata: {
          displayName: 'Teradata',
          iconClass: 'icon-teradata',
        },
        crediq: {
          displayName: 'CRED iQ',
          iconClass: 'icon-crediq',
        },
        salt: {
          displayName: 'Salt',
          iconClass: 'icon-salt',
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
      notices: {},
      searchHighlight: {
        enableHighlight: true,
      },
      sortCriterias: {
        name: {
          direction: SortDirection.descending,
          key: 'name',
          name: 'Alphabetical',
        },
        sort_order: {
          direction: SortDirection.ascending,
          key: 'sort_order',
          name: 'Table Default',
        },
      },
      stats: {
        iconNotRequiredTypes: [],
      },
      supportedDescriptionSources: {
        crediq: {
          displayName: 'CRED iQ',
          iconPath: '/static/images/icons/logo-crediq.svg',
        },
        dremio: {
          displayName: 'Dremio',
          iconPath: '/static/images/icons/logo-dremio.svg',
        },
        github: {
          displayName: 'Github',
          iconPath: '/static/images/github.png',
        },
      },
    },
    [ResourceType.user]: {
      displayName: 'People',
      searchHighlight: {
        enableHighlight: false,
      },
    },
    [ResourceType.data_provider]: {
      displayName: 'Providers',
      supportedSources: {
        sec_gov: {
          displayName: 'SEC.gov',
          iconClass: 'icon-secgov',
        },
        cmd_rvl: {
          displayName: 'CMD+RVL',
          iconClass: 'icon-cmdrvl',
        },
        egan_jones_ratings_company: {
          displayName: 'Egan-Jones Ratings',
          iconClass: 'icon-eganjones',
        },
        egan_jones_proxy_services: {
          displayName: 'Egan-Jones Proxy',
          iconClass: 'icon-eganjones',
        },
      },
      filterCategories: [
        {
          categoryId: 'name',
          displayName: 'Name',
          helpText:
            'Enter one or more comma separated values with exact file names or regex wildcard patterns',
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
      searchHighlight: {
        enableHighlight: false,
      },
    },
    [ResourceType.file]: {
      displayName: 'Files',
      supportedSources: {
        csv: {
          displayName: 'CSV',
          iconClass: 'icon-csv',
        },
        excel: {
          displayName: 'Excel',
          iconClass: 'icon-excel',
        },
        pdf: {
          displayName: 'PDF',
          iconClass: 'icon-pdf',
        },
      },
      filterCategories: [
        {
          categoryId: 'name',
          displayName: 'Name',
          helpText:
            'Enter one or more comma separated values with exact file names or regex wildcard patterns',
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
      searchHighlight: {
        enableHighlight: false,
      },
    },
  },
  searchPagination: {
    resultsPerPage: 10,
  },
  tableLineage: {
    defaultLineageDepth: 5,
    externalEnabled: false,
    iconPath: 'PATH_TO_ICON',
    inAppListEnabled: false,
    inAppPageEnabled: false,
    isBeta: false,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string
    ) =>
      `https://DEFAULT_LINEAGE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`,
  },
  tableProfile: {
    exploreUrlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string,
      partitionKey?: string,
      partitionValue?: string
    ) =>
      `https://DEFAULT_EXPLORE_URL?schema=${schema}&cluster=${cluster}&db=${database}&table=${table}`,
    isBeta: false,
    isExploreEnabled: false,
  },
  tableQualityChecks: {
    isEnabled: false,
  },
  userIdLabel: 'email address'
};

export default configDefault;
