import { testSaga } from 'redux-saga-test-plan';
import { takeEvery } from 'redux-saga/effects';

import { submitSearchResource, updateSearchState } from 'ducks/search/reducer';
import * as SearchUtils from 'ducks/search/utils';

import globalState from 'fixtures/globalState';
import { datasetFilterExample } from 'fixtures/search/filters';

import { SearchType } from 'interfaces';

import { updateFilterByCategory, UpdateSearchFilter } from './reducer';
import * as Sagas from './sagas';

describe('filter sagas', () => {
  describe('filterWatcher', () => {
    it('debounces update filter actions with filterWorker', () => {
      testSaga(Sagas.filterWatcher)
        .next()
        .is(takeEvery(UpdateSearchFilter.REQUEST, Sagas.filterWorker))
        .next()
        .isDone();
    });
  });

  describe('filterWorker', () => {
    let mockSearchStateWithFilters;
    beforeAll(() => {
      mockSearchStateWithFilters = {
        ...globalState.search,
        filters: datasetFilterExample,
      };
    });

    it('puts expected actions for updating a filter', () => {
      const testCategoryId = 'database';
      const testValue = ['hive'];
      testSaga(
        Sagas.filterWorker,
        updateFilterByCategory({
          searchFilters: [{ categoryId: testCategoryId, value: testValue }],
        })
      )
        .next()
        .select(SearchUtils.getSearchState)
        .next(globalState.search)
        .put(
          submitSearchResource({
            resource: mockSearchStateWithFilters.resource,
            resourceFilters: {
              [testCategoryId]: {
                value: testValue.join(','),
              },
            },
            searchTerm: mockSearchStateWithFilters.search_term,
            pageIndex: 0,
            searchType: SearchType.FILTER,
            updateUrl: true,
          })
        )
        .next()
        .isDone();
    });

    it('updates the state instead of doing a search when search term and filters are empty', () => {
      const testCategoryId = 'database';
      const expectedFilters = { table: {} };
      testSaga(
        Sagas.filterWorker,
        updateFilterByCategory({
          searchFilters: [{ categoryId: testCategoryId, value: undefined }],
        })
      )
        .next()
        .select(SearchUtils.getSearchState)
        .next({ ...globalState.search, search_term: '' })
        .put(
          updateSearchState({
            filters: expectedFilters,
            resource: mockSearchStateWithFilters.resource,
            updateUrl: true,
            submitSearch: false,
            clearResourceResults: true,
          })
        )
        .next()
        .isDone();
    });

    it('removes any cleared values from the current state', () => {
      const testCategoryId = 'database';
      const expectedFilters = { table: {} };
      const mockStateWithEmptyFilter = {
        ...mockSearchStateWithFilters,
        search_term: '',
        filters: { table: { [testCategoryId]: { value: undefined } } },
      };
      testSaga(
        Sagas.filterWorker,
        updateFilterByCategory({ searchFilters: [] })
      )
        .next()
        .select(SearchUtils.getSearchState)
        .next(mockStateWithEmptyFilter)
        .put(
          updateSearchState({
            filters: expectedFilters,
            resource: mockSearchStateWithFilters.resource,
            updateUrl: true,
            submitSearch: false,
            clearResourceResults: true,
          })
        )
        .next()
        .isDone();
    });
  });
});
