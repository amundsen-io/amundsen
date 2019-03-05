import { PreviewData, PreviewQueryParams, TableMetadata, User } from '../../components/TableDetail/types';
import { UpdateTagData, Tag } from '../../components/Tags/types';
import { UpdateMethod } from '../../components/OwnerEditor/types';
export { PreviewData, PreviewQueryParams, TableMetadata, Tag, User, UpdateMethod, UpdateTagData };

type MessageResponse = { msg: string };
type TableData = TableMetadata & {
  owners: User[];
  tags: Tag[]; 
};
export type DescriptionResponse = { description: string; } & MessageResponse;
export type LastIndexedResponse = { timestamp: string; } & MessageResponse;

export type PreviewDataResponse = { previewData: PreviewData; } & MessageResponse;
export type TableDataResponse = { tableData: TableData; } & MessageResponse;

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
export interface GetTableDataResponse {
  type: GetTableData.SUCCESS | GetTableData.FAILURE;
  payload: {
    statusCode: number;
    data: TableMetadata;
    owners: { [id: string] : User };
    tags: Tag[];
  }
}

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
export interface GetTableDescriptionResponse {
  type: GetTableDescription.SUCCESS | GetTableDescription.FAILURE;
  payload: TableMetadata;
}

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
export interface UpdateTableDescriptionResponse {
  type: UpdateTableDescription.SUCCESS | UpdateTableDescription.FAILURE;
}

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
export interface GetColumnDescriptionResponse {
  type: GetColumnDescription.SUCCESS | GetColumnDescription.FAILURE;
  payload: TableMetadata;
}

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
export interface UpdateColumnDescriptionResponse {
  type: UpdateColumnDescription.SUCCESS | UpdateColumnDescription.FAILURE;
}

/* getLastIndexed */
export enum GetLastIndexed {
  ACTION = 'amundsen/tableMetadata/GET_LAST_UPDATED',
  SUCCESS = 'amundsen/tableMetadata/GET_LAST_UPDATED_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/GET_LAST_UPDATED_FAILURE',
}
export interface GetLastIndexedRequest {
  type: GetLastIndexed.ACTION;
}
export interface GetLastIndexedResponse {
  type: GetLastIndexed.SUCCESS | GetLastIndexed.FAILURE;
  payload?: number;
}

/* getPreviewData */
export interface PreviewDataState {
  data: PreviewData;
  status: number | null;
}
export enum GetPreviewData {
  ACTION = 'amundsen/preview/GET_PREVIEW_DATA',
  SUCCESS = 'amundsen/preview/GET_PREVIEW_DATA_SUCCESS',
  FAILURE = 'amundsen/preview/GET_PREVIEW_DATA_FAILURE',
}
export interface GetPreviewDataRequest {
  type: GetPreviewData.ACTION;
  queryParams: PreviewQueryParams;
}
export interface GetPreviewDataResponse {
  type: GetPreviewData.SUCCESS | GetPreviewData.FAILURE;
  payload: PreviewDataState;
}

/* updateTableOwner */
export interface UpdatePayload {
  method: UpdateMethod;
  id: string;
}
export enum UpdateTableOwner {
  ACTION = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER',
  SUCCESS = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER_SUCCESS',
  FAILURE = 'amundsen/tableMetadata/UPDATE_TABLE_OWNER_FAILURE',
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
export interface UpdateTagsResponse {
  type: UpdateTags.SUCCESS | UpdateTags.FAILURE,
  payload: Tag[];
}
