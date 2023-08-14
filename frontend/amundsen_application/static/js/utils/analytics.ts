// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import Analytics, { AnalyticsInstance } from 'analytics';

import * as ConfigUtils from 'config/config-utils';
import { pageViewActionType } from 'ducks/ui';
import {
  ActionLogParams,
  ClickLogParams,
  postActionLog,
} from 'ducks/log/api/v0';

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

  // Leaving this here as it is unvaluable when working on event tracking
  // console.log('!!! trackEvent: ', eventName, properties);

  if (eventName === pageViewActionType) {
    analytics.page({
      url: properties.label,
    });
  } else {
    analytics.track(eventName, properties);
  }
};

export function logAction(declaredProps: ActionLogParams) {
  const props = {
    location: window.location.pathname,
    ...declaredProps,
  };

  postActionLog(props);
  trackEvent(declaredProps.command, props);
}

/**
 * Computes the type of node from the HTML element on the event
 * @param target  HTML element clicked
 * @returns       The type of node it was clicked
 */
export function getNodeName(target: EventTarget & HTMLElement): string {
  let result = target.nodeName.toLowerCase();

  if (result === 'a') {
    if (target.classList.contains?.('btn')) {
      result = 'button';
    } else {
      result = 'link';
    }
  }

  return result;
}

export function logClick(
  event: React.MouseEvent<HTMLElement>,
  declaredProps?: ClickLogParams
) {
  const target = event.currentTarget;
  const label = target.innerText || target.textContent || '';
  // eslint-disable-next-line @typescript-eslint/tslint/config, @typescript-eslint/naming-convention
  const target_id =
    target.dataset && target.dataset.type ? target.dataset.type : target.id;
  const inferredProps: ActionLogParams = {
    command: 'click',
    target_id,
    label,
    target_type: getNodeName(target),
  };

  if (target.nodeValue !== null) {
    inferredProps.value = target.nodeValue;
  }

  logAction({ ...inferredProps, ...declaredProps });
}
