import {
  GetTableData, GetTableDataRequest, GetTableDataResponse,
  UpdateTableOwner, UpdateTableOwnerRequest, UpdateTableOwnerResponse,
  UpdatePayload, User
} from '../types';

export type TableOwnerReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  UpdateTableOwnerRequest | UpdateTableOwnerResponse ;

export interface TableOwnerReducerState {
  isLoading: boolean;
  owners: { [id: string] : User };
}

export function updateTableOwner(updateArray: UpdatePayload[], onSuccess?: () => any, onFailure?: () => any): UpdateTableOwnerRequest {
  return {
    onSuccess,
    onFailure,
    updateArray,
    type: UpdateTableOwner.ACTION,
  };
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
