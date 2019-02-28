import { GetTableData, GetTableDataRequest, GetTableDataResponse } from '../reducer';
import { User } from '../../../components/TableDetail/types';

/* updateTableOwner */
export enum UpdateTableOwner {
  ACTION = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER',
  SUCCESS = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER_FAILURE',
}

export enum UpdateMethod {
  PUT = 'PUT',
  DELETE = 'DELETE',
}

export interface UpdateTableOwnerRequest {
  type: UpdateTableOwner.ACTION;
  method: UpdateMethod;
  value: string;
  onSuccess?: () => any;
  onFailure?: () => any;
}

interface UpdateTableOwnerResponse {
  type: UpdateTableOwner.SUCCESS | UpdateTableOwner.FAILURE;
}

export function updateTableOwner(value: string, method: UpdateMethod, onSuccess?: () => any, onFailure?: () => any): UpdateTableOwnerRequest {
  return {
    value,
    method,
    onSuccess,
    onFailure,
    type: UpdateTableOwner.ACTION,
  };
}
/* end updateTableOwner */

export type TableOwnerReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  UpdateTableOwnerRequest | UpdateTableOwnerResponse;

export interface TableOwnerReducerState {
  isLoading: boolean;
  owners: User[];
}

export const initialOwnersState: TableOwnerReducerState = {
  isLoading: true,
  owners: [],
};

export default function reducer(state: TableOwnerReducerState = initialOwnersState, action: TableOwnerReducerAction): TableOwnerReducerState {
  switch (action.type) {
    case GetTableData.ACTION:
      return { isLoading: true, owners: [] };
    case GetTableData.FAILURE:
    case GetTableData.SUCCESS:
      return { isLoading: false, owners: action.payload.owners };
    default:
      return state;
  }
}
