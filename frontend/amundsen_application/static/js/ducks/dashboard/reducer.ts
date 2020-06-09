import {
  GetDashboard,
  GetDashboardRequest,
  GetDashboardResponse,
  GetDashboardPayload,
} from 'ducks/dashboard/types';
import { DashboardMetadata } from 'interfaces/Dashboard';

/* Actions */

export function getDashboard(payload: {
  uri: string;
  searchIndex?: string;
  source?: string;
}): GetDashboardRequest {
  return {
    payload,
    type: GetDashboard.REQUEST,
  };
}

export function getDashboardSuccess(payload: GetDashboardPayload) {
  return {
    payload,
    type: GetDashboard.SUCCESS,
  };
}

export function getDashboardFailure(
  payload: GetDashboardPayload
): GetDashboardResponse {
  return {
    payload,
    type: GetDashboard.FAILURE,
  };
}

/* Reducer */

export interface DashboardReducerState {
  isLoading: boolean;
  statusCode: number;
  dashboard: DashboardMetadata;
}

export const initialDashboardState: DashboardMetadata = {
  badges: [],
  chart_names: [],
  cluster: '',
  created_timestamp: null,
  description: '',
  frequent_users: [],
  group_name: '',
  group_url: '',
  last_run_state: '',
  last_run_timestamp: null,
  last_successful_run_timestamp: null,
  name: '',
  owners: [],
  product: '',
  queries: [],
  recent_view_count: null,
  tables: [],
  tags: [],
  updated_timestamp: null,
  uri: '',
  url: '',
};

export const initialState: DashboardReducerState = {
  isLoading: true,
  statusCode: null,
  dashboard: initialDashboardState,
};

export default function reducer(
  state: DashboardReducerState = initialState,
  action
): DashboardReducerState {
  switch (action.type) {
    case GetDashboard.REQUEST:
      return {
        ...state,
        statusCode: null,
        isLoading: true,
      };
    case GetDashboard.FAILURE:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        dashboard: initialDashboardState,
      };
    case GetDashboard.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        dashboard: action.payload.dashboard,
      };
    default:
      return state;
  }
}
