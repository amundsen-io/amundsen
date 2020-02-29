import { ResourceType } from 'interfaces';

import reducer, {
  clearAllFilters,
  clearFilterByCategory,
  setSearchInputByResource,
  updateFilterByCategory,
  initialFilterState,
  FilterReducerState,
  UpdateSearchFilter,
} from '../reducer';

describe('filters ducks', () => {
  describe('actions', () => {
    it('clearAllFilters - returns the action to clear all filters', () => {
      const action = clearAllFilters();
      expect(action.type).toBe(UpdateSearchFilter.CLEAR_ALL);
    });

    it('clearFilterByCategory - returns the action to clear the filters for a given category', () => {
      const testCategory = 'category';
      const action = clearFilterByCategory(testCategory);
      const { payload } = action;
      expect(action.type).toBe(UpdateSearchFilter.CLEAR_CATEGORY);
      expect(payload.categoryId).toBe(testCategory);
    });

    it('setSearchInputByResource - returns the action to set all search input for a given resource', () => {;
      const testResource = ResourceType.table;
      const testFilters = { 'column': 'column_name' }
      const testIndex = 0;
      const testTerm = 'test';
      const action = setSearchInputByResource(testFilters, testResource, testIndex, testTerm);
      const { payload } = action;
      expect(action.type).toBe(UpdateSearchFilter.SET_BY_RESOURCE);
      expect(payload.resourceType).toBe(testResource);
      expect(payload.filters).toBe(testFilters);
      expect(payload.pageIndex).toBe(testIndex);
      expect(payload.term).toBe(testTerm);
    });

    it('updateFilterByCategory - returns the action to update the filters for a given category', () => {;
      const testCategory = 'column';
      const testValue = 'column_name';
      const action = updateFilterByCategory(testCategory, testValue);
      const { payload } = action;
      expect(action.type).toBe(UpdateSearchFilter.UPDATE_CATEGORY);
      expect(payload.categoryId).toBe(testCategory);
      expect(payload.value).toBe(testValue);
    });
  });

  describe('reducer', () => {
    let testState: FilterReducerState;
    beforeAll(() => {
      testState = {
        [ResourceType.table]: {
          'column': 'column_name'
        }
      }
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' }, ResourceType.table)).toBe(testState);
    });

    it('returns initial reducer state on UpdateSearchFilter.CLEAR_ALL', () => {
      expect(reducer(testState, clearAllFilters(), ResourceType.table)).toBe(initialFilterState);
    });

    it('removes the given category from the current resource filter state on UpdateSearchFilter.CLEAR_CATEGORY', () => {
      const givenResource = ResourceType.table;
      const givenCategory = 'column';
      expect(testState[givenResource][givenCategory]).toBeTruthy();
      const result = reducer(testState, clearFilterByCategory(givenCategory), givenResource);
      expect(result[givenResource][givenCategory]).toBe(undefined);
    });

    it('sets the given filters on the given resource on UpdateSearchFilter.SET_BY_RESOURCE', () => {
      const givenResource = ResourceType.table;
      const givenFilters = {
        'column': 'column_name',
        'schema': 'schema_name',
        'database': { 'testDb': true }
      }
      const result = reducer(initialFilterState, setSearchInputByResource(givenFilters, givenResource), givenResource);
      expect(result[givenResource]).toBe(givenFilters);
    });

    it('sets the given category on the filter state to the given value on UpdateSearchFilter.UPDATE_CATEGORY', () => {
      const givenResource = ResourceType.table;
      const givenCategory = 'database';
      const givenValue = { 'testDb': true }
      const result = reducer(initialFilterState, updateFilterByCategory(givenCategory, givenValue), givenResource);
      expect(result[givenResource][givenCategory]).toBe(givenValue);
    });
  });
});
