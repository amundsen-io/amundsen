// This file should be used to add new config variables or overwrite defaults from config-default.ts

import { AppConfigCustom, BadgeStyle } from './config-types';

const configCustom: AppConfigCustom = {
  browse: {
    curatedTags: [],
    showAllTags: true,
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
    enabled: false,
  },
  indexFeatures: {
    enabled: false,
  },
  userIdLabel: 'email address',
  issueTracking: {
    enabled: false,
  },
  badges: {
    pii: {
      style: BadgeStyle.WARNING,
      displayName: 'PII',
    },
  },
};

export default configCustom;
