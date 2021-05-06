import { ColumnLineageMap, Lineage } from 'interfaces/Lineage';
import {
  GetColumnLineage,
  GetColumnLineageRequest,
  GetColumnLineageResponse,
  GetTableLineage,
  GetTableLineageRequest,
  GetTableLineageResponse,
  GetTableColumnLineage,
  GetTableColumnLineageRequest,
  GetTableColumnLineageResponse,
} from './types';

export const initialLineageState = {
  lineageTree: {
    upstream_entities: [],
    downstream_entities: [],
  },
  status: null,
};

export const emptyLineageTree = {
  upstream_entities: [],
  downstream_entities: [],
};

export const initialState: LineageReducerState = {
  lineage: initialLineageState,
  // ToDo: Please remove once list based view is deprecated
  columnLineageMap: {},
};

/* ACTIONS */
export function getTableLineage(key: string): GetTableLineageRequest {
  return {
    type: GetTableLineage.REQUEST,
    payload: { key },
  };
}

export function getTableLineageSuccess(
  data: Lineage,
  status: number
): GetTableLineageResponse {
  return {
    type: GetTableLineage.SUCCESS,
    payload: {
      lineage: data,
      status,
    },
  };
}

export function getTableLineageFailure(
  status: number
): GetTableLineageResponse {
  return {
    type: GetTableLineage.FAILURE,
    payload: {
      lineage: initialLineageState.lineageTree,
      status,
    },
  };
}

export function getColumnLineage(
  key: string,
  columnName: string
): GetColumnLineageRequest {
  return {
    type: GetColumnLineage.REQUEST,
    payload: { key, columnName },
    meta: {
      analytics: {
        name: `getColumnLineage`,
        payload: {
          category: 'lineage',
          label: `${key}/${columnName}`,
        },
      },
    },
  };
}

export function getColumnLineageSuccess(
  data: Lineage,
  status: number
): GetColumnLineageResponse {
  return {
    type: GetColumnLineage.SUCCESS,
    payload: {
      lineage: data,
      status,
    },
  };
}

export function getColumnLineageFailure(
  status: number
): GetColumnLineageResponse {
  return {
    type: GetColumnLineage.FAILURE,
    payload: {
      lineage: initialLineageState.lineageTree,
      status,
    },
  };
}

// ToDo: Please remove once list based view is deprecated
export function getTableColumnLineage(
  key: string,
  columnName: string
): GetTableColumnLineageRequest {
  return {
    type: GetTableColumnLineage.REQUEST,
    payload: { key, columnName },
    meta: {
      analytics: {
        name: `getTableColumnLineage`,
        payload: {
          category: 'lineage',
          label: `${key}/${columnName}`,
        },
      },
    },
  };
}

// ToDo: Please remove once list based view is deprecated
export function getTableColumnLineageSuccess(
  data: Lineage,
  columnName: string,
  status: number
): GetTableColumnLineageResponse {
  return {
    type: GetTableColumnLineage.SUCCESS,
    payload: {
      columnName,
      status,
      lineage: data,
    },
  };
}
// ToDo: Please remove once list based view is deprecated
export function getTableColumnLineageFailure(
  columnName: string,
  status: number
): GetTableColumnLineageResponse {
  return {
    type: GetTableColumnLineage.FAILURE,
    payload: {
      columnName,
      lineage: initialLineageState.lineageTree,
      status,
    },
  };
}

/* REDUCER */
export interface LineageReducerState {
  lineage: {
    status: number | null;
    lineageTree: Lineage;
  };
  // ToDo: Please remove once list based view is deprecated
  columnLineageMap: ColumnLineageMap;
}

export default function reducer(
  state: LineageReducerState = initialState,
  action
): LineageReducerState {
  switch (action.type) {
    case GetTableLineage.SUCCESS:
    case GetTableLineage.FAILURE:
      return {
        ...state,
        lineage: {
          lineageTree: (<GetTableLineageResponse>action).payload.lineage,
          status: (<GetTableLineageResponse>action).payload.status,
        },
      };
    case GetColumnLineage.SUCCESS:
    case GetColumnLineage.FAILURE:
      return {
        ...state,
        lineage: {
          lineageTree: (<GetColumnLineageResponse>action).payload.lineage,
          status: (<GetColumnLineageResponse>action).payload.status,
        },
      };
    // ToDo: Please remove once list based view is deprecated
    case GetTableColumnLineage.REQUEST: {
      const { columnName } = (<GetTableColumnLineageRequest>action).payload;
      return {
        ...state,
        columnLineageMap: {
          ...state.columnLineageMap,
          [columnName]: {
            lineage: emptyLineageTree,
            isLoading: true,
          },
        },
      };
    }
    // ToDo: Please remove once list based view is deprecated
    case GetTableColumnLineage.SUCCESS:
    case GetTableColumnLineage.FAILURE: {
      const { columnName, lineage: columnLineage } = (<
        GetTableColumnLineageResponse
      >action).payload;
      return {
        ...state,
        columnLineageMap: {
          ...state.columnLineageMap,
          [columnName]: {
            lineage: columnLineage,
            isLoading: false,
          },
        },
      };
    }
    default:
      return state;
  }
}
