import { GetTableData, GetTableDataRequest, GetTableDataResponse } from '../reducer';
import { UpdateMethod } from '.../../../components/OwnerEditor/types';
import { User } from '.../../../components/TableDetail/types';

/* updateTableOwner */
export enum UpdateTableOwner {
  ACTION = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER',
  SUCCESS = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER_FAILURE',
}

interface UpdatePayload {
  method: UpdateMethod;
  id: string;
}

export interface UpdateTableOwnerRequest {
  type: UpdateTableOwner.ACTION;
  updateArray: UpdatePayload[];
  onSuccess?: () => any;
  onFailure?: () => any;
}

export interface UpdateTableOwnerResponse {
  type: UpdateTableOwner.SUCCESS | UpdateTableOwner.FAILURE;
  payload: { [id: string] : User };
}

export function updateTableOwner(updateArray: UpdatePayload[], onSuccess?: () => any, onFailure?: () => any): UpdateTableOwnerRequest {
  return {
    onSuccess,
    onFailure,
    updateArray,
    type: UpdateTableOwner.ACTION,
  };
}
/* end updateTableOwner */

export type TableOwnerReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  UpdateTableOwnerRequest | UpdateTableOwnerResponse;

export interface TableOwnerReducerState {
  isLoading: boolean;
  owners: { [id: string] : User };
}

export const initialOwnersState: TableOwnerReducerState = {
  isLoading: true,
  owners: {},
};

export default function reducer(state: TableOwnerReducerState = initialOwnersState, action: TableOwnerReducerAction): TableOwnerReducerState {
  switch (action.type) {
    case GetTableData.ACTION:
      return { isLoading: true, owners: {} };
    case GetTableData.FAILURE:
    case GetTableData.SUCCESS:
      return { isLoading: false, owners: action.payload.owners };
    case UpdateTableOwner.ACTION:
      return { ...state, isLoading: true };
    case UpdateTableOwner.FAILURE:
    case UpdateTableOwner.SUCCESS:
      return { isLoading: false, owners: action.payload };
    default:
      return state;
  }
}
