// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { SnowflakeTableShare, SnowflakeTableShares } from 'interfaces/Snowflake';
import {
  GetSnowflakeTableShares,
  GetSnowflakeTableSharesRequest,
  GetSnowflakeTableSharesResponse
} from './types';


export const initialSnowflakeTableSharesState = [
    {
      owner_account: '',
      name: '',
      listing: {
        global_name: '',
        name: '',
        title: '',
        subtitle: '',
        description: ''
      }
    }
  ]


export const initialState: SnowflakeTableSharesReducerState = {
  isLoading: false,
  snowflakeTableShares: initialSnowflakeTableSharesState
};

/* ACTIONS */
export function getSnowflakeTableShares(tableUri: string): GetSnowflakeTableSharesRequest {
  return { 
    payload: { tableUri: tableUri },
    type: GetSnowflakeTableShares.REQUEST 
  };
}
export function getSnowflakeTableSharesFailure(): GetSnowflakeTableSharesResponse {
  return { 
    type: GetSnowflakeTableShares.FAILURE, 
    payload: { snowflakeTableShares: initialSnowflakeTableSharesState } 
  };
}
export function getSnowflakeTableSharesSuccess(snowflakeTableShares: SnowflakeTableShare[]): GetSnowflakeTableSharesResponse {
  return { 
    type: GetSnowflakeTableShares.SUCCESS, 
    payload: { snowflakeTableShares } 
  };
}

/* REDUCER */
export interface SnowflakeTableSharesReducerState {
  isLoading: boolean;
  snowflakeTableShares: SnowflakeTableShare[];
}

export default function reducer(
  state: SnowflakeTableSharesReducerState = initialState,
  action
): SnowflakeTableSharesReducerState {
  switch (action.type) {
    case GetSnowflakeTableShares.REQUEST:
      return {
        isLoading: true,
        snowflakeTableShares: state.snowflakeTableShares
      };
    case GetSnowflakeTableShares.FAILURE:
      return initialState;
    case GetSnowflakeTableShares.SUCCESS:
      return {
        isLoading: false,
        snowflakeTableShares: (<GetSnowflakeTableSharesResponse>action).payload.snowflakeTableShares
      };
    default:
      return state;
  }
}
