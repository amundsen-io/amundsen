import { ResourceType, SearchType } from 'interfaces';

import { submitSearchResource } from 'ducks/search/reducer';

import reducer, {
  updateFilterByCategory,
  initialFilterState,
  FilterReducerState,
  UpdateSearchFilter,
} from './reducer';

describe('filters reducer', () => {
  describe('actions', () => {
    it('updateFilterByCategory - returns the action to update the filters for a given category', () => {
      const testCategory = 'column';
      const testValues = ['column_name'];
      const testOperation = 'OR';
      const action = updateFilterByCategory({
        categoryId: testCategory,
        values: testValues,
        operation: testOperation,
      });
      const { payload } = action;
      expect(action.type).toBe(UpdateSearchFilter.REQUEST);
      expect(payload.categoryId).toBe(testCategory);
      expect(payload.values).toBe(testValues);
      expect(payload.operation).toBe(testOperation);
    });
  });

  describe('reducer', () => {
    let testState: FilterReducerState;
    beforeAll(() => {
      testState = {
        column: {
          values: ['column_name'],
          operation: 'OR',
        },
      };
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toBe(testState);
    });

    describe('handles SubmitSearchResource.REQUEST', () => {
      it('updates the filter state if request contains filter information', () => {
        const givenResource = ResourceType.table;
        const givenFilters = { database: {values: ['testDb'], operation: 'OR' } };
        const result = reducer(
          initialFilterState,
          submitSearchResource({
            resource: givenResource,
            resourceFilters: givenFilters,
            searchTerm: 'test',
            pageIndex: 0,
            searchType: SearchType.FILTER,
            updateUrl: true,
          })
        );
        console.log(result);
        expect(result['database']).toBe(givenFilters);
      });

      it('does not update the filter state if request does not contains filter information', () => {
        const result = reducer(
          testState,
          submitSearchResource({
            pageIndex: 1,
            searchType: SearchType.PAGINATION,
            updateUrl: true,
          })
        );
        expect(result).toBe(testState);
      });
    });
  });
});
