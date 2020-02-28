// This file should be used to add new config variables or overwrite defaults from config-default.ts

import { AppConfigCustom } from './config-types';

const configCustom: AppConfigCustom = {
  browse: {
    curatedTags: [],
    showAllTags: true,
  },
  google: {
    enabled: false,
    key: 'default-key',
    sampleRate: 100,
  },
  mailClientFeatures: {
    feedbackEnabled: false,
    notificationsEnabled: false,
  },
  indexUsers: {
    enabled: false,
  }, 
  issueTracking: {
    enabled: false
  }
};

export default configCustom;
