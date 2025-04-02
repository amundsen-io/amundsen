// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { ResourceType } from 'interfaces/Resources';
import { LogSearchEvent, LogSearchEventRequest } from './types';

export function logSearchEvent(
  resourceLink: string,
  resourceType: ResourceType,
  source: string,
  index: number,
  event: any,
  inline: boolean,
  extra?: { [key: string]: any }
): LogSearchEventRequest {
  return {
    type: LogSearchEvent.REQUEST,
    payload: {
      resourceLink,
      resourceType,
      event,
      source,
      index,
      inline,
      extra,
    },
  };
}
