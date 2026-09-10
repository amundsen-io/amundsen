// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { SagaIterator } from 'redux-saga';
import { call, put, select, takeEvery } from 'redux-saga/effects';
import { logClick } from 'utils/analytics';
import { GlobalState } from 'ducks/rootReducer';
import { getPageIndex, getResults } from 'ducks/search/utils';
import { ResourceType } from 'interfaces/Resources';
import { LogSearchEvent, LogSearchEventRequest } from './types';

export function* logSearchEventWorker(
  action: LogSearchEventRequest
): SagaIterator {
  const { resourceLink, resourceType, source, index, event, inline, extra } =
    action.payload;
  const state: GlobalState = yield select();

  try {
    const makeKeyMap = (resourceType: ResourceType) => {
      switch (resourceType) {
        case ResourceType.table:
          return (table) => table.key;
        case ResourceType.feature:
          return (feature) => feature.key;
        case ResourceType.user:
          return (user) => user.user_id;
        case ResourceType.dashboard:
          return (dashboard) => dashboard.uri;
        default:
          return (a) => a;
      }
    };

    // logClick isn't an async, it just kicks off the axios post, so this doesn't need call.
    yield call(logClick, event, {
      value: source,
      position: index.toString(),
      resource_href: resourceLink,
      resource_type: resourceType,
      search_page_index: inline ? 0 : getPageIndex(state.search, resourceType),
      search_term: state.search.search_term,
      search_results: getResults(
        inline ? state.search.inlineResults : state.search,
        resourceType
      )?.results.map(makeKeyMap(resourceType)),
      ...extra,
    });
    yield put({
      type: LogSearchEvent.SUCCESS,
      payload: {
        completed: true,
      },
    });
  } catch (error) {
    yield put({
      type: LogSearchEvent.FAILURE,
      payload: {
        completed: false,
      },
    });
  }
}
export function* logSearchEventWatcher(): SagaIterator {
  yield takeEvery(LogSearchEvent.REQUEST, logSearchEventWorker);
}
