import { testSaga, expectSaga } from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';
import globalState from 'fixtures/globalState';


import * as API from '../api/v0';

import reducer, { 
  createIssue, 
  createIssueSuccess, 
  createIssueFailure, 
  getIssues, 
  getIssuesSuccess, 
  getIssuesFailure,
  IssueReducerState
} from '../reducer'; 

import {
  CreateIssue, 
  GetIssues,
  GetIssuesRequest,
  CreateIssueRequest
} from '../types'; 
import { Issue } from 'interfaces';
import { getIssuesWatcher, getIssuesWorker, createIssueWatcher, createIssueWorker } from '../sagas';
import { throwError } from 'redux-saga-test-plan/providers';

describe('issue ducks', () => {
  let formData: FormData; 
  let tableKey: string; 
  let issue: Issue; 
  let issues: Issue[]; 
  let remaining: number; 
  let remainingUrl: string; 
  beforeAll(() => {
    tableKey = 'key'; 
    const testData = { 
      key: 'table', 
      title: 'stuff', 
      description: 'This is a test' 
    };
    formData = new FormData();
    Object.keys(testData).forEach(key => formData.append(key, testData[key]));

    issue =  {
      issue_key: 'issue_key', 
      title: 'title', 
      url: 'http://url'
    }; 

    issues = [issue];
    remaining = 0; 
    remainingUrl = 'testurl'; 
  }); 

  describe('actions', () => {
    it('getIssues - returns the action to submit feedback', () => {
      const action = getIssues(tableKey);
      const { payload } = action;
      expect(action.type).toBe(GetIssues.REQUEST);
      expect(payload.key).toBe(tableKey);
    });

    it('getIssuesSuccess - returns the action to process success', () => {
      const action = getIssuesSuccess(issues, remaining, remainingUrl);
      expect(action.type).toBe(GetIssues.SUCCESS);
    });

    it('getIssuesFailure - returns the action to process failure', () => {
      const action = getIssuesFailure(null);
      expect(action.type).toBe(GetIssues.FAILURE);
    });

    it('createIssue - returns the action to create items', () => {
      const action = createIssue(formData);
      const { payload } = action;
      expect(action.type).toBe(CreateIssue.REQUEST);
      expect(payload.data).toBe(formData);
    });

    it('createIssueFailure - returns the action to process failure', () => {
      const action = createIssueFailure(null);
      const { payload } = action;
      expect(action.type).toBe(CreateIssue.FAILURE);
      expect(payload.issue).toBe(null);
    });

    it('createIssueSuccess - returns the action to process success', () => {
      const action = createIssueSuccess(issue);
      const { payload } = action;
      expect(action.type).toBe(CreateIssue.SUCCESS);
      expect(payload.issue).toBe(issue);
    });
  });

  describe('reducer', () => {
    let testState: IssueReducerState;
    let remainingUrl: string; 
    let remaining: number; 
    beforeAll(() => {
      const stateIssues: Issue[]=[];
      remaining = 0; 
      remainingUrl = 'testUrl'; 
      testState = { 
        isLoading: false, 
        issues: stateIssues, 
        remainingIssues: remaining, 
        remainingIssuesUrl: remainingUrl
      };
     
    });

    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
    });

    it('should handle GetIssues.REQUEST', () => {
      expect(reducer(testState, getIssues(tableKey))).toEqual({ 
        issues: [], 
        isLoading: true, 
        remainingIssuesUrl: null, 
        remainingIssues: 0
      });
    });

    it('should handle GetIssues.SUCCESS', () => {
      expect(reducer(testState, getIssuesSuccess(issues, remaining, remainingUrl))).toEqual({ 
        issues, 
        isLoading: false,
        remainingIssues: remaining, 
        remainingIssuesUrl: remainingUrl
      });
    });

    it('should handle GetIssues.FAILURE', () => {
      expect(reducer(testState, getIssuesFailure([], 0, null))).toEqual({ 
        issues: [], 
        isLoading: false, 
        remainingIssuesUrl: null,
        remainingIssues: remaining 
      });
    });

    it('should handle CreateIssue.REQUEST', () => {
      expect(reducer(testState, createIssue(formData))).toEqual({ 
        issues: [], 
        isLoading: true, 
        remainingIssuesUrl: remainingUrl,
        remainingIssues: remaining 
       });
    });

    it('should handle CreateIssue.SUCCESS', () => {
      expect(reducer(testState, createIssueSuccess(issue))).toEqual({
         ...testState, issues: [issue], isLoading: false });
    });

    it('should handle CreateIssue.FAILURE', () => {
      expect(reducer(testState, createIssueFailure(null))).toEqual({ issues: [], 
        isLoading: false, 
        remainingIssuesUrl: remainingUrl,
        remainingIssues: remaining 
      });
    });
  });

  describe('sagas', () => {
    describe('getIssuesWatcher', () => {
      it('takes every getIssues.REQUEST with getIssuesWatcher', () => {
        testSaga(getIssuesWatcher)
          .next().takeEvery(GetIssues.REQUEST, getIssuesWorker)
          .next().isDone();
      });
    });

    describe('getIssuesWorker', () => {
      let action: GetIssuesRequest;
      let remainingIssuesUrl: string;
      let remainingIssues: number; 
      beforeAll(() => {
        action = getIssues(tableKey);
        issues = globalState.issue.issues;
        remainingIssues = globalState.issue.remainingIssues; 
        remainingIssuesUrl = globalState.issue.remainingIssuesUrl;
      });

      it('gets issues', () => {
        return expectSaga(getIssuesWorker, action)
          .provide([
            [matchers.call.fn(API.getIssues), {issues, remainingIssues, remainingIssuesUrl}],
          ])
          .put(getIssuesSuccess(issues))
          .run();
      });

      it('handles request error', () => {
        return expectSaga(getIssuesWorker, action)
          .provide([
            [matchers.call.fn(API.getIssues), throwError(new Error())],
          ])
          .put(getIssuesFailure([], 0, null))
          .run();
      });
    });

    describe('createIssueWatcher', () => {
      it('takes every createIssue.REQUEST with getIssuesWatcher', () => {
        testSaga(createIssueWatcher)
          .next().takeEvery(CreateIssue.REQUEST, createIssueWorker)
          .next().isDone();
      });
    });

    describe('createIssuesWorker', () => {
      let action: CreateIssueRequest;
      beforeAll(() => {
        action = createIssue(formData);
        issues = [issue];
      });

      it('creates a issue', () => {
        return expectSaga(createIssueWorker, action)
          .provide([
            [matchers.call.fn(API.createIssue), issue],
          ])
          .put(createIssueSuccess(issue))
          .run();
      });

      it('handles request error', () => {
        return expectSaga(createIssueWorker, action)
          .provide([
            [matchers.call.fn(API.createIssue), throwError(new Error())],
          ])
          .put(createIssueFailure(null))
          .run();
      });
    });

  });
}); 
