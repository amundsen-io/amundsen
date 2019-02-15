import { AppConfig } from "./config.types";

const configDefault: AppConfig = {
  browse: {
    curatedTags: [],
    showAllTags: true,
  },
  google: {
    key: 'default-key',
    sampleRate: 100,
  },
  logoPath: null,
  navLinks: [
    {
      label: "Announcements",
      href: "/announcements",
      use_router: true,
    },
    {
      label: "Browse",
      href: "/browse",
      use_router: true,
    }
  ],
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
