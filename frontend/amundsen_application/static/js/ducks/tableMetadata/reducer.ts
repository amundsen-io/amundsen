import { PreviewData, PreviewQueryParams, TableMetadata } from 'interfaces';

import {
  GetTableData, GetTableDataRequest, GetTableDataResponse,
  GetTableDescription, GetTableDescriptionRequest, GetTableDescriptionResponse,
  UpdateTableDescription, UpdateTableDescriptionRequest, UpdateTableDescriptionResponse,
  GetColumnDescription, GetColumnDescriptionResponse, GetColumnDescriptionRequest,
  UpdateColumnDescription, UpdateColumnDescriptionRequest, UpdateColumnDescriptionResponse,
  GetLastIndexed, GetLastIndexedRequest, GetLastIndexedResponse,
  GetPreviewData, GetPreviewDataRequest, GetPreviewDataResponse,
  UpdateTableOwner,
  UpdateTags,
} from './types';

import tableOwnersReducer, { initialOwnersState, TableOwnerReducerState } from './owners/reducer';

import tableTagsReducer, { initialTagsState,  TableTagsReducerState } from './tags/reducer';

/* ACTIONS */
export function getTableData(key: string, searchIndex?: string, source?: string): GetTableDataRequest {
  return {
    key,
    searchIndex,
    source,
    type: GetTableData.REQUEST,
  };
};
export function getTableDescription(onSuccess?: () => any, onFailure?: () => any): GetTableDescriptionRequest {
  return {
    onSuccess,
    onFailure,
    type: GetTableDescription.REQUEST,
  };
};
export function updateTableDescription(newValue: string, onSuccess?: () => any, onFailure?: () => any): UpdateTableDescriptionRequest {
  return {
    newValue,
    onSuccess,
    onFailure,
    type: UpdateTableDescription.REQUEST,
  };
};
export function getColumnDescription(columnIndex: number, onSuccess?: () => any, onFailure?: () => any): GetColumnDescriptionRequest {
  return {
    onSuccess,
    onFailure,
    columnIndex,
    type: GetColumnDescription.REQUEST,
  };
};
export function updateColumnDescription(newValue: string, columnIndex: number, onSuccess?: () => any, onFailure?: () => any): UpdateColumnDescriptionRequest {
  return {
    newValue,
    columnIndex,
    onSuccess,
    onFailure,
    type: UpdateColumnDescription.REQUEST,
  };
};
export function getLastIndexed(): GetLastIndexedRequest {
  return { type: GetLastIndexed.REQUEST };
};
export function getPreviewData(queryParams: PreviewQueryParams): GetPreviewDataRequest {
  return { queryParams, type: GetPreviewData.REQUEST };
};

/* REDUCER */
export interface TableMetadataReducerState {
  isLoading: boolean;
  lastIndexed: number;
  preview: {
    data: PreviewData;
    status: number | null;
  };
  statusCode: number;
  tableData: TableMetadata;
  tableOwners: TableOwnerReducerState;
  tableTags: TableTagsReducerState;
};

const initialPreviewState = {
  data: {},
  status: null,
};

const initialTableDataState: TableMetadata = {
  cluster: '',
  columns: [],
  database: '',
  is_editable: false,
  is_view: false,
  key: '',
  schema: '',
  table_name: '',
  table_description: '',
  table_writer: { application_url: '', description: '', id: '', name: '' },
  partition: { is_partitioned: false },
  table_readers: [],
  source: { source: '', source_type: '' },
  watermarks: [],
};

const initialState: TableMetadataReducerState = {
  isLoading: true,
  lastIndexed: null,
  preview: initialPreviewState,
  statusCode: null,
  tableData: initialTableDataState,
  tableOwners: initialOwnersState,
  tableTags: initialTagsState,
};

export default function reducer(state: TableMetadataReducerState = initialState, action): TableMetadataReducerState {
  switch (action.type) {
    case GetTableData.REQUEST:
      return {
        ...state,
        isLoading: true,
        preview: initialPreviewState,
        tableData: initialTableDataState,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
        tableTags: tableTagsReducer(state.tableTags, action),
      };
    case GetTableData.FAILURE:
      return {
        ...state,
        isLoading: false,
        preview: initialPreviewState,
        statusCode: (<GetTableDataResponse>action).payload.statusCode,
        tableData: initialTableDataState,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
        tableTags: tableTagsReducer(state.tableTags, action),
      };
    case GetTableData.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: (<GetTableDataResponse>action).payload.statusCode,
        tableData: (<GetTableDataResponse>action).payload.data,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
        tableTags: tableTagsReducer(state.tableTags, action),
      };
    case GetTableDescription.FAILURE:
    case GetTableDescription.SUCCESS:
      return { ...state, tableData: (<GetTableDescriptionResponse>action).payload.tableMetadata };
    case GetColumnDescription.FAILURE:
    case GetColumnDescription.SUCCESS:
      return { ...state, tableData: (<GetColumnDescriptionResponse>action).payload.tableMetadata };
    case GetLastIndexed.FAILURE:
      return { ...state, lastIndexed: null };
    case GetLastIndexed.SUCCESS:
      return { ...state, lastIndexed: (<GetLastIndexedResponse>action).payload.lastIndexedEpoch };
    case GetPreviewData.FAILURE:
      return { ...state, preview: initialPreviewState };
    case GetPreviewData.SUCCESS:
      return { ...state, preview: (<GetPreviewDataResponse>action).payload };
    case UpdateTableOwner.REQUEST:
    case UpdateTableOwner.FAILURE:
    case UpdateTableOwner.SUCCESS:
      return { ...state, tableOwners: tableOwnersReducer(state.tableOwners, action) };
    case UpdateTags.REQUEST:
    case UpdateTags.FAILURE:
    case UpdateTags.SUCCESS:
      return { ...state, tableTags: tableTagsReducer(state.tableTags, action) };
    default:
      return state;
  }
}
