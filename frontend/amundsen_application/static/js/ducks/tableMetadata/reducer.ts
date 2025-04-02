import {
  DashboardResource,
  OwnerDict,
  PreviewData,
  TablePreviewQueryParams,
  TableMetadata,
  TableQualityChecks,
  Tag,
} from 'interfaces';

import {
  ClickTableQualityLink,
  ClickTableQualityLinkRequest,
  GetColumnDescription,
  GetColumnDescriptionRequest,
  GetColumnDescriptionResponse,
  GetTypeMetadataDescription,
  GetTypeMetadataDescriptionRequest,
  GetTypeMetadataDescriptionResponse,
  GetPreviewData,
  GetPreviewDataRequest,
  GetPreviewDataResponse,
  GetTableDashboards,
  GetTableDashboardsResponse,
  GetTableData,
  GetTableDataRequest,
  GetTableDataResponse,
  GetTableDescription,
  GetTableDescriptionRequest,
  GetTableDescriptionResponse,
  GetTableQualityChecks,
  GetTableQualityChecksRequest,
  GetTableQualityChecksResponse,
  UpdateColumnDescription,
  UpdateColumnDescriptionRequest,
  UpdateTypeMetadataDescription,
  UpdateTypeMetadataDescriptionRequest,
  UpdateTableDescription,
  UpdateTableDescriptionRequest,
  UpdateTableOwner,
} from './types';

import tableOwnersReducer, {
  initialOwnersState,
  TableOwnerReducerState,
} from './owners/reducer';

import { STATUS_CODES } from '../../constants';

export const initialPreviewState = {
  data: {},
  status: null,
};

export const initialTableDataState: TableMetadata = {
  badges: [],
  cluster: '',
  columns: [],
  database: '',
  is_editable: false,
  is_view: false,
  key: '',
  last_updated_timestamp: 0,
  schema: '',
  name: '',
  description: '',
  table_writer: { application_url: '', description: '', id: '', name: '' },
  table_apps: [],
  partition: { is_partitioned: false },
  table_readers: [],
  source: { source: '', source_type: '' },
  resource_reports: [],
  watermarks: [],
  programmatic_descriptions: {},
};

export const emptyQualityChecks = {
  external_url: '',
  last_run_timestamp: 0,
  num_checks_success: 0,
  num_checks_failed: 0,
  num_checks_total: 0,
};

export const initialQualityChecksState = {
  status: null,
  isLoading: false,
  checks: emptyQualityChecks,
};

export const initialState: TableMetadataReducerState = {
  isLoading: true,
  preview: initialPreviewState,
  statusCode: null,
  tableData: initialTableDataState,
  tableOwners: initialOwnersState,
  tableQualityChecks: initialQualityChecksState,
};

/* ACTIONS */
export function getTableData(
  key: string,
  searchIndex?: string,
  source?: string
): GetTableDataRequest {
  return {
    payload: {
      key,
      searchIndex,
      source,
    },
    type: GetTableData.REQUEST,
  };
}
export function getTableDataFailure(): GetTableDataResponse {
  return {
    type: GetTableData.FAILURE,
    payload: {
      data: initialTableDataState,
      owners: {},
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
      tags: [],
    },
  };
}
export function getTableDataSuccess(
  data: TableMetadata,
  owners: OwnerDict,
  statusCode: number,
  tags: Tag[]
): GetTableDataResponse {
  return {
    type: GetTableData.SUCCESS,
    payload: {
      data,
      owners,
      statusCode,
      tags,
    },
  };
}

export function getTableDashboardsResponse(
  dashboards: DashboardResource[],
  errorMessage: string = ''
): GetTableDashboardsResponse {
  return {
    type: GetTableDashboards.RESPONSE,
    payload: {
      dashboards,
      errorMessage,
    },
  };
}

export function getTableDescription(
  onSuccess?: () => any,
  onFailure?: () => any
): GetTableDescriptionRequest {
  return {
    payload: {
      onSuccess,
      onFailure,
    },
    type: GetTableDescription.REQUEST,
  };
}
export function getTableDescriptionFailure(
  tableMetadata: TableMetadata
): GetTableDescriptionResponse {
  return {
    type: GetTableDescription.FAILURE,
    payload: {
      tableMetadata,
    },
  };
}
export function getTableDescriptionSuccess(
  tableMetadata: TableMetadata
): GetTableDescriptionResponse {
  return {
    type: GetTableDescription.SUCCESS,
    payload: {
      tableMetadata,
    },
  };
}

export function updateTableDescription(
  newValue: string,
  onSuccess?: () => any,
  onFailure?: () => any
): UpdateTableDescriptionRequest {
  return {
    payload: {
      newValue,
      onSuccess,
      onFailure,
    },
    type: UpdateTableDescription.REQUEST,
  };
}

export function getColumnDescription(
  columnKey: string,
  onSuccess?: () => any,
  onFailure?: () => any
): GetColumnDescriptionRequest {
  return {
    payload: {
      onSuccess,
      onFailure,
      columnKey,
    },
    type: GetColumnDescription.REQUEST,
  };
}
export function getColumnDescriptionFailure(
  tableMetadata: TableMetadata
): GetColumnDescriptionResponse {
  return {
    type: GetColumnDescription.FAILURE,
    payload: {
      tableMetadata,
    },
  };
}
export function getColumnDescriptionSuccess(
  tableMetadata: TableMetadata
): GetColumnDescriptionResponse {
  return {
    type: GetColumnDescription.SUCCESS,
    payload: {
      tableMetadata,
    },
  };
}

export function updateColumnDescription(
  newValue: string,
  columnKey: string,
  onSuccess?: () => any,
  onFailure?: () => any
): UpdateColumnDescriptionRequest {
  return {
    payload: {
      newValue,
      columnKey,
      onSuccess,
      onFailure,
    },
    type: UpdateColumnDescription.REQUEST,
  };
}

export function getTypeMetadataDescription(
  typeMetadataKey: string,
  onSuccess?: () => any,
  onFailure?: () => any
): GetTypeMetadataDescriptionRequest {
  return {
    payload: {
      onSuccess,
      onFailure,
      typeMetadataKey,
    },
    type: GetTypeMetadataDescription.REQUEST,
  };
}
export function getTypeMetadataDescriptionFailure(
  tableMetadata: TableMetadata
): GetTypeMetadataDescriptionResponse {
  return {
    type: GetTypeMetadataDescription.FAILURE,
    payload: {
      tableMetadata,
    },
  };
}
export function getTypeMetadataDescriptionSuccess(
  tableMetadata: TableMetadata
): GetTypeMetadataDescriptionResponse {
  return {
    type: GetTypeMetadataDescription.SUCCESS,
    payload: {
      tableMetadata,
    },
  };
}

export function updateTypeMetadataDescription(
  newValue: string,
  typeMetadataKey: string,
  onSuccess?: () => any,
  onFailure?: () => any
): UpdateTypeMetadataDescriptionRequest {
  return {
    payload: {
      newValue,
      typeMetadataKey,
      onSuccess,
      onFailure,
    },
    type: UpdateTypeMetadataDescription.REQUEST,
  };
}

export function getPreviewData(
  queryParams: TablePreviewQueryParams
): GetPreviewDataRequest {
  return { payload: { queryParams }, type: GetPreviewData.REQUEST };
}
export function getPreviewDataFailure(
  data: PreviewData,
  status: number
): GetPreviewDataResponse {
  return {
    type: GetPreviewData.FAILURE,
    payload: {
      data,
      status,
    },
  };
}
export function getPreviewDataSuccess(
  data: PreviewData,
  status: number
): GetPreviewDataResponse {
  return {
    type: GetPreviewData.SUCCESS,
    payload: {
      data,
      status,
    },
  };
}

export function getTableQualityChecks(
  key: string
): GetTableQualityChecksRequest {
  return {
    type: GetTableQualityChecks.REQUEST,
    payload: {
      key,
    },
  };
}
export function getTableQualityChecksSuccess(
  checks: TableQualityChecks,
  status: number
): GetTableQualityChecksResponse {
  return {
    type: GetTableQualityChecks.SUCCESS,
    payload: {
      checks,
      status,
    },
  };
}
export function getTableQualityChecksFailure(
  status: number
): GetTableQualityChecksResponse {
  return {
    type: GetTableQualityChecks.FAILURE,
    payload: {
      status,
      checks: emptyQualityChecks,
    },
  };
}

export function clickDataQualityLink(): ClickTableQualityLinkRequest {
  return {
    type: ClickTableQualityLink.REQUEST,
    meta: {
      analytics: {
        name: 'table/clickTableQualityLink',
        payload: {
          action: 'click',
          category: 'table',
          label: 'see more',
        },
      },
    },
  };
}

/* REDUCER */
export interface TableMetadataReducerState {
  dashboards?: {
    isLoading: boolean;
    dashboards: DashboardResource[];
    errorMessage?: string;
  };
  isLoading: boolean;
  preview: {
    data: PreviewData;
    status: number | null;
  };
  statusCode: number | null;
  tableData: TableMetadata;
  tableOwners: TableOwnerReducerState;
  tableQualityChecks: {
    status: number | null;
    isLoading: boolean;
    checks: TableQualityChecks;
  };
}

export default function reducer(
  state: TableMetadataReducerState = initialState,
  action
): TableMetadataReducerState {
  switch (action.type) {
    case GetTableDashboards.RESPONSE:
      return {
        ...state,
        dashboards: {
          isLoading: false,
          dashboards: action.payload.dashboards,
          errorMessage: action.payload.errorMessage,
        },
      };
    case GetTableData.REQUEST:
      return initialState;
    case GetTableData.FAILURE:
      return {
        ...state,
        isLoading: false,
        preview: initialPreviewState,
        statusCode: (<GetTableDataResponse>action).payload.statusCode,
        tableData: initialTableDataState,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
      };
    case GetTableData.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: (<GetTableDataResponse>action).payload.statusCode,
        tableData: (<GetTableDataResponse>action).payload.data,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
      };
    case GetTableDescription.FAILURE:
    case GetTableDescription.SUCCESS:
      return {
        ...state,
        tableData: (<GetTableDescriptionResponse>action).payload.tableMetadata,
      };
    case GetColumnDescription.FAILURE:
    case GetColumnDescription.SUCCESS:
      return {
        ...state,
        tableData: (<GetColumnDescriptionResponse>action).payload.tableMetadata,
      };
    case GetTypeMetadataDescription.FAILURE:
    case GetTypeMetadataDescription.SUCCESS:
      return {
        ...state,
        tableData: (<GetTypeMetadataDescriptionResponse>action).payload
          .tableMetadata,
      };
    case GetPreviewData.FAILURE:
    case GetPreviewData.SUCCESS:
      return { ...state, preview: (<GetPreviewDataResponse>action).payload };
    case UpdateTableOwner.REQUEST:
    case UpdateTableOwner.FAILURE:
    case UpdateTableOwner.SUCCESS:
      return {
        ...state,
        tableOwners: tableOwnersReducer(state.tableOwners, action),
      };
    case GetTableQualityChecks.REQUEST:
      return {
        ...state,
        tableQualityChecks: {
          status: null,
          isLoading: true,
          checks: emptyQualityChecks,
        },
      };
    case GetTableQualityChecks.SUCCESS:
    case GetTableQualityChecks.FAILURE:
      const { checks, status } = (<GetTableQualityChecksResponse>action)
        .payload;

      return {
        ...state,
        tableQualityChecks: {
          status,
          checks,
          isLoading: false,
        },
      };
    default:
      return state;
  }
}
