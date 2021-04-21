// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import Analytics, { AnalyticsInstance } from 'analytics';

import * as ConfigUtils from 'config/config-utils';
import { pageViewActionType } from 'ducks/ui';

let sharedAnalyticsInstance;

export const analyticsInstance = (): AnalyticsInstance => {
  if (sharedAnalyticsInstance) {
    return sharedAnalyticsInstance;
  }

  const { plugins } = ConfigUtils.getAnalyticsConfig();

  sharedAnalyticsInstance = Analytics({
    app: 'amundsen',
    version: '100',
    plugins,
  });

  return sharedAnalyticsInstance;
};

export const trackEvent = (
  eventName: string,
  properties: Record<string, any>
) => {
  const analytics = analyticsInstance();

  if (eventName === pageViewActionType) {
    analytics.page({
      url: properties.label,
    });
  } else {
    analytics.track(eventName, properties);
  }
};
