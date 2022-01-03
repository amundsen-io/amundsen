import { Issue, CreateIssuePayload, NotificationPayload } from 'interfaces';
import {
  GetIssues,
  CreateIssue,
  GetIssuesResponse,
  CreateIssueRequest,
  GetIssuesRequest,
  CreateIssueResponse,
} from './types';

/* ACTIONS */
export function createIssue(
  createIssuePayload: CreateIssuePayload,
  notificationPayload: NotificationPayload
): CreateIssueRequest {
  return {
    payload: {
      createIssuePayload,
      notificationPayload,
    },
    type: CreateIssue.REQUEST,
  };
}

export function createIssueSuccess(issue: Issue): CreateIssueResponse {
  return {
    type: CreateIssue.SUCCESS,
    payload: {
      issue,
    },
  };
}

export function createIssueFailure(issue?: Issue): CreateIssueResponse {
  return {
    type: CreateIssue.FAILURE,
    payload: {
      issue,
    },
  };
}

export function getIssues(tableKey: string): GetIssuesRequest {
  return {
    type: GetIssues.REQUEST,
    payload: {
      key: tableKey,
    },
  };
}

export function getIssuesSuccess(
  issues: Issue[],
  total?: number,
  openCount?: number,
  allIssuesUrl?: string,
  openIssuesUrl?: string,
  closedIssuesUrl?: string
): GetIssuesResponse {
  return {
    type: GetIssues.SUCCESS,
    payload: {
      issues,
      total,
      openCount,
      allIssuesUrl,
      openIssuesUrl,
      closedIssuesUrl,
    },
  };
}

export function getIssuesFailure(
  issues: Issue[],
  total?: number,
  openCount?: number,
  allIssuesUrl?: string,
  openIssuesUrl?: string,
  closedIssuesUrl?: string
): GetIssuesResponse {
  return {
    type: GetIssues.FAILURE,
    payload: {
      issues,
      total,
      openCount,
      allIssuesUrl,
      openIssuesUrl,
      closedIssuesUrl,
    },
  };
}

/* REDUCER */
export interface IssueReducerState {
  issues: Issue[];
  allIssuesUrl?: string;
  openIssuesUrl?: string;
  closedIssuesUrl?: string;
  total?: number;
  openCount?: number;
  isLoading: boolean;
  createIssueFailure: boolean;
}

export const initialIssuestate: IssueReducerState = {
  issues: [],
  allIssuesUrl: undefined,
  openIssuesUrl: undefined,
  closedIssuesUrl: undefined,
  total: 0,
  openCount: 0,
  isLoading: false,
  createIssueFailure: false,
};

export default function reducer(
  state: IssueReducerState = initialIssuestate,
  action
): IssueReducerState {
  switch (action.type) {
    case GetIssues.REQUEST:
      return {
        ...initialIssuestate,
        isLoading: true,
        createIssueFailure: false,
      };
    case GetIssues.FAILURE:
      return { ...initialIssuestate };
    case GetIssues.SUCCESS:
      return {
        ...state,
        ...(<GetIssuesResponse>action).payload,
        isLoading: false,
        createIssueFailure: false,
      };
    case CreateIssue.REQUEST:
      return { ...state, isLoading: true, createIssueFailure: false };
    case CreateIssue.FAILURE:
      return { ...state, isLoading: false, createIssueFailure: true };
    case CreateIssue.SUCCESS:
      const { issue } = (<CreateIssueResponse>action).payload;
      if (issue === undefined) {
        throw Error('payload.issue must be set for CreateIssue.SUCCESS');
      }
      return {
        ...state,
        issues: [issue, ...state.issues],
        isLoading: false,
        createIssueFailure: false,
      };
    default:
      return state;
  }
}
