// This file should be used to add new config variables or overwrite defaults from config-default.ts

import { AppConfigCustom, BadgeStyle } from './config-types';

const configCustom: AppConfigCustom = {
  browse: {
    curatedTags: [],
    showAllTags: true,
    showBadgesInHome: true,
  },
  analytics: {
    plugins: [],
  },
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  indexDashboards: {
    enabled: false,
  },
  indexUsers: {
    enabled: true,
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
  announcements: {
    enabled: true
  },
  tableProfile: {
    isBeta: false,
    isExploreEnabled: true,
    exploreUrlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string,
    ) => {
      return `https://metabase.revolutlabs.com/dashboard/3366?schema=${schema}&table_name=${table}`;
    },
  },
  tableLineage: {
    iconPath: '/static/images/metabase.svg',
    isBeta: true,
    externalEnabled: true,
    inAppListEnabled: true,
    inAppPageEnabled: true,
    urlGenerator: (
      database: string,
      cluster: string,
      schema: string,
      table: string
    ) => {
      return `https://metabase.revolutlabs.com/dashboard/6780?schema_name=${schema}&table_name=${table}`;
    },
  },
  badges: {
        'deprecated': {
            style: BadgeStyle.DEFAULT,
            displayName: 'Alpha',
        },
        'partition column': {
            style: BadgeStyle.DEFAULT,
            displayName: 'Partition Column',
        },
        'sensitive': {
            style: BadgeStyle.DEFAULT,
            displayName: 'Sensitive',
        },
        'confidential': {
            style: BadgeStyle.DEFAULT,
            displayName: 'Confidential',
        },
        'critical': {
            style: BadgeStyle.PRIMARY,
            displayName: 'Critical',
        },
        'golden': {
            style: BadgeStyle.SUCCESS,
            displayName: 'Golden',
        },
   },
};

export default configCustom;
