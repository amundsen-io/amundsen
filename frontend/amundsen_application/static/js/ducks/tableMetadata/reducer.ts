import {
  GetTableData, GetTableDataRequest, GetTableDataResponse, TableMetadata,
  GetTableDescription, GetTableDescriptionRequest, GetTableDescriptionResponse,
  UpdateTableDescription, UpdateTableDescriptionRequest, UpdateTableDescriptionResponse,
  GetColumnDescription, GetColumnDescriptionResponse, GetColumnDescriptionRequest,
  UpdateColumnDescription, UpdateColumnDescriptionRequest, UpdateColumnDescriptionResponse,
  GetLastIndexed, GetLastIndexedRequest, GetLastIndexedResponse,
  GetPreviewData, GetPreviewDataRequest, GetPreviewDataResponse, PreviewQueryParams, PreviewDataState,
  UpdateTableOwner,
  UpdateTags,
} from './types';

import tableOwnersReducer, {
  initialOwnersState, TableOwnerReducerAction, TableOwnerReducerState,
} from './owners/reducer';

import tableTagsReducer, {
  initialTagsState, TableTagsReducerAction, TableTagsReducerState,
} from './tags/reducer';

export type TableMetadataReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  GetTableDescriptionRequest | GetTableDescriptionResponse |
  UpdateTableDescriptionRequest | UpdateTableDescriptionResponse |
  GetColumnDescriptionRequest | GetColumnDescriptionResponse |
  UpdateColumnDescriptionRequest | UpdateColumnDescriptionResponse |
  GetLastIndexedRequest | GetLastIndexedResponse |
  GetPreviewDataRequest | GetPreviewDataResponse |
  TableOwnerReducerAction | TableTagsReducerAction ;

export interface TableMetadataReducerState {
  isLoading: boolean;
  lastIndexed: number;
  preview: PreviewDataState;
  statusCode: number;
  tableData: TableMetadata;
  tableOwners: TableOwnerReducerState;
  tableTags: TableTagsReducerState;
}

export function getTableData(cluster: string, database: string, schema: string, tableName: string, searchIndex?: string, source?: string): GetTableDataRequest {
  return {
    cluster,
    database,
    schema,
    searchIndex,
    source,
    table_name: tableName,
    type: GetTableData.ACTION,
  };
}

export function getTableDescription(onSuccess?: () => any, onFailure?: () => any): GetTableDescriptionRequest {
  return {
    onSuccess,
    onFailure,
    type: GetTableDescription.ACTION,
  };
}

export function updateTableDescription(newValue: string, onSuccess?: () => any, onFailure?: () => any): UpdateTableDescriptionRequest {
  return {
    newValue,
    onSuccess,
    onFailure,
    type: UpdateTableDescription.ACTION,
  };
}

export function getColumnDescription(columnIndex: number, onSuccess?: () => any, onFailure?: () => any): GetColumnDescriptionRequest {
  return {
    onSuccess,
    onFailure,
    columnIndex,
    type: GetColumnDescription.ACTION,
  };
}

export function updateColumnDescription(newValue: string, columnIndex: number, onSuccess?: () => any, onFailure?: () => any): UpdateColumnDescriptionRequest {
  return {
    newValue,
    columnIndex,
    onSuccess,
    onFailure,
    type: UpdateColumnDescription.ACTION,
  };
}

export function getLastIndexed(): GetLastIndexedRequest {
  return { type: GetLastIndexed.ACTION };
}

export function getPreviewData(queryParams: PreviewQueryParams): GetPreviewDataRequest {
  return { queryParams, type: GetPreviewData.ACTION };
}

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

export default function reducer(state: TableMetadataReducerState = initialState, action: TableMetadataReducerAction): TableMetadataReducerState {
  switch (action.type) {
    case GetTableData.ACTION:
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
        statusCode: action.payload.statusCode,
        tableData: initialTableDataState,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
        tableTags: tableTagsReducer(state.tableTags, action),
      };
    case GetTableData.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        tableData: action.payload.data,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
        tableTags: tableTagsReducer(state.tableTags, action),
      };
    case GetTableDescription.FAILURE:
    case GetTableDescription.SUCCESS:
      return { ...state, tableData: action.payload };
    case GetColumnDescription.FAILURE:
    case GetColumnDescription.SUCCESS:
      return { ...state, tableData: action.payload };
    case GetLastIndexed.FAILURE:
      return { ...state, lastIndexed: null };
    case GetLastIndexed.SUCCESS:
      return { ...state, lastIndexed: action.payload };
    case GetPreviewData.FAILURE:
      return { ...state, preview: initialPreviewState };
    case GetPreviewData.SUCCESS:
      return { ...state, preview: action.payload };
    case UpdateTableOwner.ACTION:
    case UpdateTableOwner.FAILURE:
    case UpdateTableOwner.SUCCESS:
      return { ...state, tableOwners: tableOwnersReducer(state.tableOwners, action) };
    case UpdateTags.ACTION:
    case UpdateTags.FAILURE:
    case UpdateTags.SUCCESS:
      return { ...state, tableTags: tableTagsReducer(state.tableTags, action) };
    default:
      return state;
  }
}
