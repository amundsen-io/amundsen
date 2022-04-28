import { SagaIterator } from 'redux-saga';
import { takeEvery, put, select } from 'redux-saga/effects';

import { SearchType } from 'interfaces';

import { submitSearchResource, updateSearchState } from 'ducks/search/reducer';
import { getSearchState } from 'ducks/search/utils';
import { filterFromObj } from 'ducks/utilMethods';

import { UpdateSearchFilter, UpdateFilterRequest } from './reducer';

/*
 * Generates new filter shape from action payload.
 * Then executes a search on current resource based with new filters and current search state values.
 */
export function* filterWorker(action: UpdateFilterRequest): SagaIterator {
  const { searchFilters } = action.payload;
  const state = yield select(getSearchState);
  const { search_term, resource, filters } = state;
  let resourceFilters = {
    ...filters[resource],
  };

  // Remove cleared values from the current state
  const stateResourceFilters = { ...filters[resource] };
  for (const key of Object.keys(stateResourceFilters)) {
    if (stateResourceFilters[key].value === undefined) {
      delete resourceFilters[key];
    }
  }

  // Add any new filter values and remove any that have been cleared
  searchFilters.forEach((filter) => {
    if (filter.value === undefined || filter.value.length === 0) {
      resourceFilters = filterFromObj(resourceFilters, [filter.categoryId]);
    } else {
      resourceFilters[filter.categoryId] = { value: filter.value.join(',') };
    }
  });

  if (search_term || Object.keys(resourceFilters).length > 0) {
    yield put(
      submitSearchResource({
        resource,
        resourceFilters,
        searchTerm: search_term,
        pageIndex: 0,
        searchType: SearchType.FILTER,
        updateUrl: true,
      })
    );
  } else {
    const updatedFilters = { ...filters, [resource]: { ...resourceFilters } };
    yield put(
      updateSearchState({
        filters: updatedFilters,
        resource,
        updateUrl: true,
        submitSearch: false,
        clearResourceResults: true,
      })
    );
  }
}

/**
 * Listens to actions triggers by user updates to the filter state..
 */
export function* filterWatcher(): SagaIterator {
  /*
    TODO: If we want to minimize api calls on checkbox quick-select,
    we will have to debounce and accumulate filter updates elsewhere.
    To be revisited when we have more checkbox filters
  */
  yield takeEvery(UpdateSearchFilter.REQUEST, filterWorker);
}
