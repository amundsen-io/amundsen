// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { testSaga } from 'redux-saga-test-plan';

import { ResourceType } from 'interfaces/Resources';
import * as Analytics from 'utils/analytics';
import globalState from 'fixtures/globalState';
import { logSearchEvent } from './reducer';

import { logSearchEventWatcher, logSearchEventWorker } from './sagas';

import { LogSearchEvent } from './types';

const searchState = globalState.search;

describe('log ducks', () => {
  const resourceLink = '/some/resource/link';
  const resourceType = ResourceType.table;
  const source = 'source';
  const index = 1;
  const event = 'some_event';
  const inline = false;
  const extra = { key: 'value', other_key: 42 };

  const mockState = {
    search: {
      ...searchState,
    },
  };

  describe('actions', () => {
    it('logSearchEvent - returns the action to log search events', () => {
      const action = logSearchEvent(
        resourceLink,
        resourceType,
        source,
        index,
        event,
        inline,
        extra
      );
      const { payload } = action;

      expect(action.type).toBe(LogSearchEvent.REQUEST);
      expect(payload.resourceLink).toBe(resourceLink);
      expect(payload.resourceType).toBe(resourceType);
      expect(payload.source).toBe(source);
      expect(payload.index).toBe(index);
      expect(payload.event).toBe(event);
      expect(payload.inline).toBe(inline);
      expect(payload.extra).toBe(extra);
    });
  });

  describe('sagas', () => {
    describe('logSearchEventWatcher', () => {
      it('takes every LogSearchEvent.REQUEST with logSearchEventWorker', () => {
        testSaga(logSearchEventWatcher)
          .next()
          .takeEvery(LogSearchEvent.REQUEST, logSearchEventWorker)
          .next()
          .isDone();
      });
    });

    describe('logSearchEventWorker', () => {
      it('executes flow for logging search events', () => {
        testSaga(
          logSearchEventWorker,
          logSearchEvent(
            resourceLink,
            resourceType,
            source,
            index,
            event,
            inline,
            extra
          )
        )
          .next()
          .select()
          .next(mockState)
          .call(Analytics.logClick, event, {
            value: source,
            position: index.toString(),
            resource_href: resourceLink,
            resource_type: resourceType,
            search_page_index: mockState.search.tables.page_index,
            search_term: mockState.search.search_term,
            search_results: mockState.search.tables.results.map((t) => t.key),
            ...extra,
          })
          .next()
          .put({ type: LogSearchEvent.SUCCESS, payload: { completed: true } })
          .next()
          .isDone();
      });

      it('handles request error', () => {
        testSaga(
          logSearchEventWorker,
          logSearchEvent(
            resourceLink,
            resourceType,
            source,
            index,
            event,
            inline,
            extra
          )
        )
          .next()
          .select()
          .next(mockState)
          .call(Analytics.logClick, event, {
            value: source,
            position: index.toString(),
            resource_href: resourceLink,
            resource_type: resourceType,
            search_page_index: mockState.search.tables.page_index,
            search_term: mockState.search.search_term,
            search_results: mockState.search.tables.results.map((t) => t.key),
            ...extra,
          })
          .throw(new Error('error'))
          .put({ type: LogSearchEvent.FAILURE, payload: { completed: false } })
          .next()
          .isDone();
      });

      it('handles resource types correctly', () => {
        testSaga(
          logSearchEventWorker,
          logSearchEvent(
            resourceLink,
            ResourceType.dashboard,
            source,
            index,
            event,
            inline,
            extra
          )
        )
          .next()
          .select()
          .next(mockState)
          .call(Analytics.logClick, event, {
            value: source,
            position: index.toString(),
            resource_href: resourceLink,
            resource_type: ResourceType.dashboard,
            search_page_index: mockState.search.dashboards.page_index,
            search_term: mockState.search.search_term,
            search_results: mockState.search.dashboards.results.map(
              (d) => d.uri
            ),
            ...extra,
          })
          .next()
          .put({ type: LogSearchEvent.SUCCESS, payload: { completed: true } })
          .next()
          .isDone();
      });

      it('handles inline search events correctly', () => {
        testSaga(
          logSearchEventWorker,
          logSearchEvent(
            resourceLink,
            resourceType,
            source,
            index,
            event,
            true,
            extra
          )
        )
          .next()
          .select()
          .next(mockState)
          .call(Analytics.logClick, event, {
            value: source,
            position: index.toString(),
            resource_href: resourceLink,
            resource_type: resourceType,
            search_page_index: mockState.search.inlineResults.tables.page_index,
            search_term: mockState.search.search_term,
            search_results: mockState.search.inlineResults.tables.results.map(
              (t) => t.key
            ),
            ...extra,
          })
          .next()
          .put({ type: LogSearchEvent.SUCCESS, payload: { completed: true } })
          .next()
          .isDone();
      });
    });
  });
});
