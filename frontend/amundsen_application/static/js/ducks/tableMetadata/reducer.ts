import { PreviewData, PreviewQueryParams, TableMetadata } from '../../components/TableDetail/types';
import { UpdateTagData } from '../../components/Tags/types';

/* getTableData */
export enum GetTableData {
  ACTION = 'amundsen/tableMetadata/GET_TABLE_DATA',
  SUCCESS = 'amundsen/tableMetadata/GET_TABLE_DATA_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/GET_TABLE_DATA_FAILURE',
}

export interface GetTableDataRequest {
  type: GetTableData.ACTION;
  cluster: string;
  database: string;
  schema: string;
  searchIndex?: string;
  source?: string;
  table_name: string;
}

interface GetTableDataResponse {
  type: GetTableData.SUCCESS | GetTableData.FAILURE;
  payload: {
    statusCode: number;
    tableData: TableMetadata;
  }
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
/* end getTableData */

/* getTableDescription */
export enum GetTableDescription {
  ACTION = 'amundsen/tableMetadata/GET_TABLE_DESCRIPTION',
  SUCCESS = 'amundsen/tableMetadata/GET_TABLE_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/GET_TABLE_DESCRIPTION_FAILURE',
}

export interface GetTableDescriptionRequest {
  type: GetTableDescription.ACTION;
  onSuccess?: () => any;
  onFailure?: () => any;
}

interface GetTableDescriptionResponse {
  type: GetTableDescription.SUCCESS | GetTableDescription.FAILURE;
  payload: TableMetadata;
}

export function getTableDescription(onSuccess?: () => any, onFailure?: () => any): GetTableDescriptionRequest {
  return {
    onSuccess,
    onFailure,
    type: GetTableDescription.ACTION,
  };
}
/* end getTableDescription */

/* updateTableDescription */
export enum UpdateTableDescription {
  ACTION = 'amundsen/tableMetadata/UPDATE_TABLE_DESCRIPTION',
  SUCCESS = 'amundsen/tableMetadata/UPDATE_TABLE_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/UPDATE_TABLE_DESCRIPTION_FAILURE',
}

export interface UpdateTableDescriptionRequest {
  type: UpdateTableDescription.ACTION;
  newValue: string;
  onSuccess?: () => any;
  onFailure?: () => any;
}

interface UpdateTableDescriptionResponse {
  type: UpdateTableDescription.SUCCESS | UpdateTableDescription.FAILURE;
}

export function updateTableDescription(newValue: string, onSuccess?: () => any, onFailure?: () => any): UpdateTableDescriptionRequest {
  return {
    newValue,
    onSuccess,
    onFailure,
    type: UpdateTableDescription.ACTION,
  };
}
/* end updateTableDescription */

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

/* getColumnDescription */
export enum GetColumnDescription {
  ACTION = 'amundsen/tableMetadata/GET_COLUMN_DESCRIPTION',
  SUCCESS = 'amundsen/tableMetadata/GET_COLUMN_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/GET_COLUMN_DESCRIPTION_FAILURE',
}

export interface GetColumnDescriptionRequest {
  type: GetColumnDescription.ACTION;
  columnIndex: number;
  onSuccess?: () => any;
  onFailure?: () => any;
}

interface GetColumnDescriptionResponse {
  type: GetColumnDescription.SUCCESS | GetColumnDescription.FAILURE;
  payload: TableMetadata;
}

export function getColumnDescription(columnIndex: number, onSuccess?: () => any, onFailure?: () => any): GetColumnDescriptionRequest {
  return {
    onSuccess,
    onFailure,
    columnIndex,
    type: GetColumnDescription.ACTION,
  };
}
/* end getColumnDescription */

/* updateColumnDescription */
export enum UpdateColumnDescription {
  ACTION = 'amundsen/tableMetadata/UPDATE_COLUMN_DESCRIPTION',
  SUCCESS = 'amundsen/tableMetadata/UPDATE_COLUMN_DESCRIPTION_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/UPDATE_COLUMN_DESCRIPTION_FAILURE',
}

export interface UpdateColumnDescriptionRequest {
  type: UpdateColumnDescription.ACTION;
  newValue: string;
  columnIndex: number;
  onSuccess?: () => any;
  onFailure?: () => any;
}
interface UpdateColumnDescriptionResponse {
  type: UpdateColumnDescription.SUCCESS | UpdateColumnDescription.FAILURE;
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
/* end updateColumnDescription */

/* updateTags */
export enum UpdateTags {
  ACTION = 'amundsen/tags/UPDATE_TAGS',
  SUCCESS = 'amundsen/tags/UPDATE_TAGS_SUCCESS',
  FAILURE = 'amundsen/tags/UPDATE_TAGS_FAILURE',
}

export interface UpdateTagsRequest {
  type: UpdateTags.ACTION,
  tagArray: UpdateTagData[];
}
interface UpdateTagsResponse {
  type: UpdateTags.SUCCESS | UpdateTags.FAILURE,
  payload: TableMetadata;
}

export function updateTags(tagArray: UpdateTagData[]): UpdateTagsRequest  {
  return {
    tagArray,
    type: UpdateTags.ACTION,
  };
}
/* end updateTags */

/* getLastIndexed */
export enum GetLastIndexed {
  ACTION = 'amundsen/tableMetadata/GET_LAST_UPDATED',
  SUCCESS = 'amundsen/tableMetadata/GET_LAST_UPDATED_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/GET_LAST_UPDATED_FAILURE',
}

export interface GetLastIndexedRequest {
  type: GetLastIndexed.ACTION;
}

interface GetLastIndexedResponse {
  type: GetLastIndexed.SUCCESS | GetLastIndexed.FAILURE;
  payload?: number;
}

export function getLastIndexed(): GetLastIndexedRequest {
  return { type: GetLastIndexed.ACTION };
}
/* end getLastIndexed */

/* getPreviewData */
export enum GetPreviewData {
  ACTION = 'amundsen/preview/GET_PREVIEW_DATA',
  SUCCESS = 'amundsen/preview/GET_PREVIEW_DATA_SUCCESS',
  FAILURE = 'amundsen/preview/GET_PREVIEW_DATA_FAILURE',
}
interface PreviewDataState {
  data: PreviewData;
  status: number | null;
}
export interface GetPreviewDataRequest {
  type: GetPreviewData.ACTION;
  queryParams: PreviewQueryParams;
}
interface GetPreviewDataResponse {
  type: GetPreviewData.SUCCESS | GetPreviewData.FAILURE;
  payload: PreviewDataState;
}

export function getPreviewData(queryParams: PreviewQueryParams): GetPreviewDataRequest {
  return { queryParams, type: GetPreviewData.ACTION };
}
/* end getPreviewData */

export type TableMetadataReducerAction =
  GetTableDataRequest | GetTableDataResponse |
  GetTableDescriptionRequest | GetTableDescriptionResponse |
  UpdateTableDescriptionRequest | UpdateTableDescriptionResponse |
  UpdateTableOwnerRequest | UpdateTableOwnerResponse |
  GetColumnDescriptionRequest | GetColumnDescriptionResponse |
  UpdateColumnDescriptionRequest | UpdateColumnDescriptionResponse |
  UpdateTagsRequest | UpdateTagsResponse |
  GetLastIndexedRequest | GetLastIndexedResponse |
  GetPreviewDataRequest | GetPreviewDataResponse;

export interface TableMetadataReducerState {
  isLoading: boolean;
  isLoadingTags: boolean;
  lastIndexed: number;
  preview: PreviewDataState;
  statusCode: number;
  tableData: TableMetadata;
}

const initialPreviewState = {
  data: {},
  status: null,
};
const initialState: TableMetadataReducerState = {
  isLoading: true,
  isLoadingTags: true,
  lastIndexed: null,
  preview: initialPreviewState,
  statusCode: null,
  tableData: {} as TableMetadata,
};

export default function reducer(state: TableMetadataReducerState = initialState, action: TableMetadataReducerAction): TableMetadataReducerState {
  switch (action.type) {
    case GetTableData.ACTION:
      return { ...state, isLoading: true, isLoadingTags: true, preview: initialPreviewState };
    case GetTableData.FAILURE:
    case GetTableData.SUCCESS:
      return { ...state, isLoading: false, isLoadingTags: false, statusCode: action.payload.statusCode, tableData: action.payload.tableData };
    case GetTableDescription.FAILURE:
    case GetTableDescription.SUCCESS:
      return { ...state, tableData: action.payload };
    case GetColumnDescription.FAILURE:
    case GetColumnDescription.SUCCESS:
      return { ...state, tableData: action.payload };
    case GetLastIndexed.SUCCESS:
        return { ...state, lastIndexed: action.payload };
    case GetLastIndexed.FAILURE:
        return { ...state, lastIndexed: null };
    case GetPreviewData.SUCCESS:
    case GetPreviewData.FAILURE:
      return { ...state, preview: action.payload };
    case UpdateTags.FAILURE:
      return { ...state, isLoadingTags: false };
    case UpdateTags.SUCCESS:
      return { ...state, isLoadingTags: false, tableData: action.payload };
    case UpdateTags.ACTION:
      return { ...state, isLoadingTags: true };
    default:
      return state;
  }
}
