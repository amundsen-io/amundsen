// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { ResourceType } from 'interfaces/Resources';

export enum LogSearchEvent {
  REQUEST = 'amundsen/search/LOG_SEARCH_REQUEST',
  SUCCESS = 'amundsen/search/LOG_SEARCH_SUCCESS',
  FAILURE = 'amundsen/search/LOG_SEARCH_FAILURE',
}

export interface LogSearchEventRequest {
  type: LogSearchEvent.REQUEST;
  payload: {
    source: string;
    index: number;
    resourceLink: string;
    resourceType: ResourceType;
    event: any;
    inline: boolean;
    extra?: { [key: string]: any };
  };
}
export interface LogSearchEventResponse {
  type: LogSearchEvent.SUCCESS | LogSearchEvent.FAILURE;
  payload: {
    completed: boolean;
  };
}
