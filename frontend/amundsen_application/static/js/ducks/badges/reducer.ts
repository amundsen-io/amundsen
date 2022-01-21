// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { Badge } from 'interfaces';

import {
  GetAllBadges,
  GetAllBadgesRequest,
  GetAllBadgesResponse,
} from './types';

/* ACTIONS */
export function getAllBadges(): GetAllBadgesRequest {
  return { type: GetAllBadges.REQUEST };
}
export function getAllBadgesFailure(): GetAllBadgesResponse {
  return { type: GetAllBadges.FAILURE, payload: { allBadges: [] } };
}
export function getAllBadgesSuccess(allBadges: Badge[]): GetAllBadgesResponse {
  return { type: GetAllBadges.SUCCESS, payload: { allBadges } };
}

/* REDUCER */
export interface BadgesReducerState {
  allBadges: BadgeState;
}

interface BadgeState {
  isLoading: boolean;
  badges: Badge[];
}

export const initialState: BadgesReducerState = {
  allBadges: {
    isLoading: false,
    badges: [],
  },
};

export default function reducer(
  state: BadgesReducerState = initialState,
  action
): BadgesReducerState {
  switch (action.type) {
    case GetAllBadges.REQUEST:
      return {
        ...state,
        allBadges: {
          ...state.allBadges,
          isLoading: true,
          badges: [],
        },
      };
    case GetAllBadges.FAILURE:
      return initialState;
    case GetAllBadges.SUCCESS:
      return {
        ...state,
        allBadges: {
          ...state.allBadges,
          isLoading: false,
          badges: (<GetAllBadgesResponse>action).payload.allBadges,
        },
      };

    default:
      return state;
  }
}
