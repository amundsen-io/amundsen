// This file should be used to add new config variables or overwrite defaults from config-default.ts

import { AppConfigCustom } from './config-types';

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
  productTour: {
    '/': [
      {
        isFeatureTour: false,
        isShownOnFirstVisit: true,
        isShownProgrammatically: true,
        steps: [
          {
            target: '.nav-bar-left a',
            title: 'Welcome to Amundsen',
            content:
              'Hi!, welcome to Amundsen, your data discovery and catalog product!',
          },
          {
            target: '.search-bar-form .search-bar-input',
            title: 'Search for resources',
            content:
              'Here you will search for the resources you are looking for',
          },
          {
            target: '.bookmark-list-header',
            title: 'Save your bookmarks',
            content:
              'Here you will see a list of the resources you have bookmarked',
          },
        ],
      },
    ],
  },
};

export default configCustom;
