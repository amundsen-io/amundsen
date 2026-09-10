// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { Badge } from 'interfaces';

export enum GetAllBadges {
  REQUEST = 'amundsen/allBadges/GET_REQUEST',
  SUCCESS = 'amundsen/allBadges/GET_SUCCESS',
  FAILURE = 'amundsen/allBadges/GET_FAILURE',
}
export interface GetAllBadgesRequest {
  type: GetAllBadges.REQUEST;
}
export interface GetAllBadgesResponse {
  type: GetAllBadges.SUCCESS | GetAllBadges.FAILURE;
  payload: {
    allBadges: Badge[];
  };
}
