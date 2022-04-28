import AppConfig from 'config/config';

import { InputFilterCategory } from 'config/config-types';

import {
  FilterOperationType,
  FilterType,
  ResourceType,
  SearchType,
} from 'interfaces';

import { submitSearchResource } from 'ducks/search/reducer';

import reducer, {
  getDefaultFiltersForResource,
  updateFilterByCategory,
  initialFilterState,
  FilterReducerState,
  UpdateSearchFilter,
} from './reducer';

describe('filters reducer', () => {
  describe('getDefaultFiltersForResource', () => {
    it('has no default values configured', () => {
      const defaultResourceFilters = getDefaultFiltersForResource(
        ResourceType.table
      );
      const expectedResourceFilters = {};
      expect(defaultResourceFilters).toEqual(expectedResourceFilters);
    });
    it('has default values configured', () => {
      const mockInputFilterCategory: InputFilterCategory = {
        categoryId: 'schema',
        displayName: 'Schema',
        allowableOperation: FilterOperationType.OR,
        defaultValue: ['test_schema1', 'test_schema2'],
        helpText: 'test schema description',
        type: FilterType.INPUT_SELECT,
      };
      AppConfig.resourceConfig.table.filterCategories = [
        mockInputFilterCategory,
      ];
      const defaultResourceFilters = getDefaultFiltersForResource(
        ResourceType.table
      );
      const expectedResourceFilters = {
        schema: {
          value: 'test_schema1,test_schema2',
          filterOperation: FilterOperationType.OR,
        },
      };
      expect(defaultResourceFilters).toEqual(expectedResourceFilters);
    });
  });

  describe('actions', () => {
    it('updateFilterByCategory - returns the action to update the filters for a given category', () => {
      const testCategory = 'column';
      const testValue = ['column_name'];
      const action = updateFilterByCategory({
        searchFilters: [
          {
            categoryId: testCategory,
            value: testValue,
          },
        ],
      });
      const { payload } = action;
      expect(action.type).toBe(UpdateSearchFilter.REQUEST);
      expect(payload.searchFilters[0].categoryId).toBe(testCategory);
      expect(payload.searchFilters[0].value).toBe(testValue);
    });
  });

  describe('reducer', () => {
    let testState: FilterReducerState;
    beforeAll(() => {
      testState = {
        [ResourceType.table]: {
          column: { value: 'column_name' },
        },
      };
    });
    it('should return the existing state if action is not handled', () => {
      expect(reducer(testState, { type: 'INVALID.ACTION' })).toBe(testState);
    });

    describe('handles SubmitSearchResource.REQUEST', () => {
      it('updates the filter state if request contains filter information', () => {
        const givenResource = ResourceType.table;
        const givenFilters = { database: { value: 'testDb' } };
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
        expect(result[givenResource]).toBe(givenFilters);
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
