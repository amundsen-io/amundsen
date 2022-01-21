// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import * as ConfigUtils from 'config/config-utils';
import { FilterConfig } from 'config/config-types';

import { FilterOperationType, FilterType, ResourceType } from 'interfaces';

import globalState from 'fixtures/globalState';
import { GlobalState } from 'ducks/rootReducer';

import { APPLY_BTN_TEXT, CLEAR_BTN_TEXT } from './constants';

import FilterSection from './FilterSection';
import {
  mapStateToProps,
  mapDispatchToProps,
  SearchFilter,
  SearchFilterProps,
  FilterSectionItem,
  CheckboxFilterSection,
} from '.';

const globalAny: any = global;

const mockFormData = {
  database: 'database',
  column: 'column',
  schema: 'schema',
  table: 'table',
  tag: 'tag',
  get: jest.fn(),
};
mockFormData.get.mockImplementation((val) => mockFormData[val]);
function formDataMock() {
  this.append = jest.fn();
  return mockFormData;
}
globalAny.FormData = formDataMock;

describe('SearchFilter', () => {
  const setup = (propOverrides?: Partial<SearchFilterProps>) => {
    const props = {
      filterSections: [
        {
          categoryId: 'database',
          allowableOperation: FilterOperationType.OR,
          helpText: 'This is what to do',
          options: [
            {
              value: 'bigquery',
              label: 'BigQuery',
            },
            {
              value: 'hive',
              label: 'Hive',
            },
          ],
          title: 'Source',
          type: FilterType.CHECKBOX_SELECT,
        },
        {
          categoryId: 'schema',
          allowableOperation: FilterOperationType.OR,
          helpText: 'This is what to do',
          title: 'Schema',
          type: FilterType.INPUT_SELECT,
        },
      ],
      applyFilters: jest.fn(),
      clearFilters: jest.fn(),
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow<SearchFilter>(<SearchFilter {...props} />);
    return {
      props,
      wrapper,
    };
  };

  describe('onApplyChanges', () => {
    let props;
    let wrapper;
    let applyFiltersSpy;

    beforeAll(() => {
      ({ props, wrapper } = setup());
      applyFiltersSpy = jest.spyOn(props, 'applyFilters');
    });

    it('calls props.applyFilters', () => {
      applyFiltersSpy.mockClear();
      wrapper.instance().onApplyChanges({ preventDefault: jest.fn() });
      expect(applyFiltersSpy).toHaveBeenCalled();
    });
  });

  describe('onClearFilter', () => {
    let props;
    let wrapper;
    let clearFiltersSpy;

    beforeAll(() => {
      ({ props, wrapper } = setup());
      clearFiltersSpy = jest.spyOn(props, 'clearFilters');
    });

    it('calls props.clearFilter with schema categoryId', () => {
      wrapper.instance().onClearFilter();

      expect(clearFiltersSpy).toHaveBeenCalledWith([
        {
          categoryId: 'database',
          value: undefined,
        },
        {
          categoryId: 'schema',
          value: undefined,
        },
      ]);
    });
  });

  describe('createFilterSection', () => {
    let props;
    let wrapper;
    let content;
    let mockCheckboxFilterData: CheckboxFilterSection;
    let mockInputFilterData: FilterSectionItem;
    beforeAll(() => {
      ({ props, wrapper } = setup());
      [mockCheckboxFilterData, mockInputFilterData] = props.filterSections;
      content = wrapper
        .instance()
        .createFilterSection('sectionKey', mockCheckboxFilterData);
    });

    describe('renders a FilterSection', () => {
      it('FilterSection exists', () => {
        const expected = 2;
        const actual = wrapper.find(FilterSection).length;

        expect(actual).toBe(expected);
      });

      it('with correct categoryId', () => {
        expect(content.props.categoryId).toBe(
          mockCheckboxFilterData.categoryId
        );
      });

      it('with correct helpText', () => {
        expect(content.props.helpText).toBe(mockCheckboxFilterData.helpText);
      });

      it('with correct title', () => {
        expect(content.props.title).toBe(mockCheckboxFilterData.title);
      });

      it('with correct type', () => {
        expect(content.props.type).toBe(mockCheckboxFilterData.type);
      });

      it('with options if not supported for the filter type ', () => {
        expect(content.props.options).toBe(mockCheckboxFilterData.options);
      });

      it('without options if not supported for the filter type ', () => {
        content = wrapper
          .instance()
          .createFilterSection('sectionKey', mockInputFilterData);
        expect(content.props.options).toBe(undefined);
      });
    });
  });

  describe('renderFilterSections', () => {
    let props;
    let wrapper;
    let createFilterSectionSpy;

    beforeAll(() => {
      ({ props, wrapper } = setup());
      createFilterSectionSpy = jest.spyOn(
        wrapper.instance(),
        'createFilterSection'
      );
      wrapper.instance().renderFilterSections(props.filterSections);
    });

    it('calls createFilterSection with correct key and section for each props.filterSections', () => {
      props.filterSections.forEach((section) => {
        expect(createFilterSectionSpy).toHaveBeenCalledWith(
          `section:${section.categoryId}`,
          section
        );
      });
    });
  });

  describe('render', () => {
    let wrapper;
    let renderFilterSectionsSpy;
    let element;

    beforeAll(() => {
      ({ wrapper } = setup());
      renderFilterSectionsSpy = jest.spyOn(
        wrapper.instance(),
        'renderFilterSections'
      );
      wrapper.instance().render();
    });

    it('renders a form with correct onSubmit property', () => {
      element = wrapper.find('form');
      expect(element.props().onSubmit).toBe(wrapper.instance().onApplyChanges);
    });

    it('renders apply filters button', () => {
      element = wrapper.find('button').first();
      expect(element.text()).toEqual(APPLY_BTN_TEXT);
    });

    it('renders button to clear categories', () => {
      element = wrapper.find('button').at(1);
      expect(element.props().onClick).toBe(wrapper.instance().onClearFilter);
      expect(element.text()).toEqual(CLEAR_BTN_TEXT);
    });

    it('calls renderFilterSections', () => {
      expect(renderFilterSectionsSpy).toHaveBeenCalledTimes(1);
    });
  });
});

describe('mapStateToProps', () => {
  const mockHelpText = 'Help me';

  const mockSchemaId = 'schema';
  const mockSchemaValue = 'schema_name';
  const mockSchemaTitle = 'Schema';

  const mockDbId = 'database';
  const mockDbTitle = 'Source';

  const MOCK_CATEGORY_CONFIG: FilterConfig = [
    {
      categoryId: mockDbId,
      displayName: mockDbTitle,
      allowableOperation: FilterOperationType.OR,
      type: FilterType.CHECKBOX_SELECT,
      helpText: mockHelpText,
      options: [
        { value: 'bigquery', displayName: 'BigQuery' },
        { value: 'hive', displayName: 'Hive' },
      ],
    },
    {
      categoryId: mockSchemaId,
      displayName: mockSchemaTitle,
      allowableOperation: FilterOperationType.OR,
      helpText: mockHelpText,
      type: FilterType.INPUT_SELECT,
    },
  ];
  const mockStateWithFilters: GlobalState = {
    ...globalState,
    search: {
      ...globalState.search,
      resource: ResourceType.table,
      filters: {
        [ResourceType.table]: {
          [mockSchemaId]: { value: mockSchemaValue },
          [mockDbId]: { value: 'hive' },
        },
      },
    },
  };
  let getFilterConfigByResourceSpy;
  let result;

  it('calls getFilterConfigByResource with resource', () => {
    getFilterConfigByResourceSpy = jest
      .spyOn(ConfigUtils, 'getFilterConfigByResource')
      .mockReturnValue(MOCK_CATEGORY_CONFIG);
    mapStateToProps(mockStateWithFilters);
    expect(getFilterConfigByResourceSpy).toHaveBeenCalledWith(
      mockStateWithFilters.search.resource
    );
  });

  it('sets expected filterSections on the result', () => {
    getFilterConfigByResourceSpy = jest
      .spyOn(ConfigUtils, 'getFilterConfigByResource')
      .mockReturnValue(MOCK_CATEGORY_CONFIG);
    result = mapStateToProps(mockStateWithFilters);
    expect(result.filterSections).toEqual([
      {
        categoryId: mockDbId,
        allowableOperation: FilterOperationType.OR,
        helpText: mockHelpText,
        options: [
          { label: 'BigQuery', value: 'bigquery' },
          { label: 'Hive', value: 'hive' },
        ],
        type: FilterType.CHECKBOX_SELECT,
        title: mockDbTitle,
      },
      {
        categoryId: mockSchemaId,
        allowableOperation: FilterOperationType.OR,
        helpText: mockHelpText,
        options: [],
        title: mockSchemaTitle,
        type: FilterType.INPUT_SELECT,
      },
    ]);
  });

  it('sets empty array on filterSections if there are no configured filterCategories', () => {
    getFilterConfigByResourceSpy = jest
      .spyOn(ConfigUtils, 'getFilterConfigByResource')
      .mockReturnValue(undefined);
    result = mapStateToProps(globalState);
    expect(result.filterSections).toEqual([]);
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;

  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets applyFilters on the props', () => {
    expect(result.applyFilters).toBeInstanceOf(Function);
  });

  it('sets clearFilters on the props', () => {
    expect(result.clearFilters).toBeInstanceOf(Function);
  });
});
