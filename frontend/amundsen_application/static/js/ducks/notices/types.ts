// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { DynamicResourceNotice } from 'interfaces';

export enum GetNotices {
  REQUEST = 'amundsen/notices/GET_NOTICES_REQUEST',
  SUCCESS = 'amundsen/notices/GET_NOTICES_SUCCESS',
  FAILURE = 'amundsen/notices/GET_NOTICES_FAILURE',
}

export interface GetNoticesRequest {
  type: GetNotices.REQUEST;
  payload: {
    key: string;
  };
}

export interface GetNoticesResponse {
  type: GetNotices.SUCCESS | GetNotices.FAILURE;
  payload: GetNoticesPayload;
}

export interface GetNoticesPayload {
  notices?: DynamicResourceNotice[];
  statusCode?: number;
  statusMessage?: string;
}
