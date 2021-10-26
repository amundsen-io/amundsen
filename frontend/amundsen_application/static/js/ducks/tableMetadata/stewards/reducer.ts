import { StewardDict, UpdateStewardPayload } from 'interfaces';

import {
  GetTableData,
  GetTableDataResponse,
  UpdateTableSteward,
  UpdateTableStewardRequest,
  UpdateTableStewardResponse,
} from '../types';

/* ACTIONS */
export function updateTableSteward(
  updateArray: UpdateStewardPayload[],
  onSuccess?: () => any,
  onFailure?: () => any
): UpdateTableStewardRequest {
  console.log('updateTableSteward', updateArray);
  return {
    payload: {
      onSuccess,
      onFailure,
      updateArray,
    },
    type: UpdateTableSteward.REQUEST,
  };
}
export function updateTableStewardFailure(
  stewards: StewardDict
): UpdateTableStewardResponse {
  return {
    type: UpdateTableSteward.FAILURE,
    payload: {
      stewards,
    },
  };
}
export function updateTableStewardSuccess(
  stewards: StewardDict
): UpdateTableStewardResponse {
  return {
    type: UpdateTableSteward.SUCCESS,
    payload: {
      stewards,
    },
  };
}

/* REDUCER */
export interface TableStewardReducerState {
  isLoading: boolean;
  stewards: StewardDict;
}

export const initialStewardsState: TableStewardReducerState = {
  isLoading: true,
  stewards: {},
};

export default function reducer(
  state: TableStewardReducerState = initialStewardsState,
  action
): TableStewardReducerState {
  switch (action.type) {
    case GetTableData.REQUEST:
      return { isLoading: true, stewards: {} };
    case GetTableData.FAILURE:
    case GetTableData.SUCCESS:
      return {
        isLoading: false,
        stewards: (<GetTableDataResponse>action).payload.stewards,
      };
    case UpdateTableSteward.REQUEST:
      console.log('UpdateTableSteward.REQUEST:');
      return { ...state, isLoading: true };
    case UpdateTableSteward.FAILURE:
    case UpdateTableSteward.SUCCESS:
      return {
        isLoading: false,
        stewards: (<UpdateTableStewardResponse>action).payload.stewards,
      };
    default:
      return state;
  }
}
