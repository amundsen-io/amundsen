// This file should be used to add new config variables or overwrite defaults from config-default.ts

import { AppConfigCustom } from './config-types';

const configCustom: AppConfigCustom = {
  
  browse: {
    curatedTags: [],
    showAllTags: true,
    showBadgesInHome: true,
    hideNonClickableBadges: false,
  },
  analytics: {
    plugins: [],
  },
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  indexDashboards: {
    enabled: true,
  },
  indexUsers: {
    enabled: true,
  },
  indexFeatures: {
    enabled: false,
  },
  indexServices: {
    enabled: true,
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
    enabled: false,
  },
  productTour: {},
  logoPath: '/static/images/favicons/prod/careem_image_1.png',
  logoTitle: 'Navigator',
  documentTitle: 'Navigator - Discovery Portal',
};

export default configCustom;
