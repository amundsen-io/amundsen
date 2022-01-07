// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import CheckBoxItem from 'components/Inputs/CheckBoxItem';

import globalState from 'fixtures/globalState';

import { GlobalState } from 'ducks/rootReducer';

import { ResourceType } from 'interfaces';
import {
  CheckBoxFilter,
  CheckBoxFilterProps,
  mapDispatchToProps,
  mapStateToProps,
} from '.';

describe('CheckBoxFilter', () => {
  const setup = (propOverrides?: Partial<CheckBoxFilterProps>) => {
    const props: CheckBoxFilterProps = {
      categoryId: 'database',
      checkboxProperties: [
        {
          label: 'BigQuery',
          value: 'bigquery',
        },
        {
          label: 'Hive',
          value: 'hive',
        },
      ],
      checkedValues: ['hive'],
      applyFilters: jest.fn(),
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow<CheckBoxFilter>(<CheckBoxFilter {...props} />);
    return {
      props,
      wrapper,
    };
  };

  describe('createCheckBoxItem', () => {
    const mockCategoryId = 'categoryId';
    let props;
    let wrapper;

    let checkBoxItem;
    let mockProperties;
    beforeAll(() => {
      ({ props, wrapper } = setup());
      [mockProperties] = props.checkboxProperties;
      const content = wrapper
        .instance()
        .createCheckBoxItem(mockCategoryId, 'testKey', mockProperties);
      checkBoxItem = shallow(<div>{content}</div>).find(CheckBoxItem);
    });

    it('returns a CheckBoxItem', () => {
      expect(checkBoxItem.exists()).toBe(true);
    });

    it('returns a CheckBoxItem with correct props', () => {
      const itemProps = checkBoxItem.props();
      expect(itemProps.checked).toBe(
        props.checkedValues.includes(mockProperties.value)
      );
      expect(itemProps.name).toBe(mockCategoryId);
      expect(itemProps.value).toBe(mockProperties.value);
      expect(itemProps.onChange).toBe(wrapper.instance().onCheckboxChange);
    });

    it('returns a CheckBoxItem with correct labelText as child', () => {
      expect(checkBoxItem.children().text()).toBe(mockProperties.label);
    });
  });

  describe('onCheckboxChange', () => {
    const mockCategoryId = 'database';
    let props;
    let wrapper;
    let mockEvent;

    let applyFiltersSpy;
    beforeAll(() => {
      ({ props, wrapper } = setup());
      applyFiltersSpy = jest.spyOn(props, 'applyFilters');
    });

    it('calls props.applyFilters if no items will be checked', () => {
      applyFiltersSpy.mockClear();
      mockEvent = {
        target: { name: mockCategoryId, value: 'hive', checked: false },
      };
      wrapper.instance().onCheckboxChange(mockEvent);
      expect(applyFiltersSpy).toHaveBeenCalledWith(mockCategoryId, []);
    });

    it('calls props.applyFilters with expected parameters', () => {
      applyFiltersSpy.mockClear();
      mockEvent = {
        target: { name: mockCategoryId, value: 'bigquery', checked: true },
      };
      const expectedCheckedValues = [...props.checkedValues, 'bigquery'];
      wrapper.instance().onCheckboxChange(mockEvent);
      expect(applyFiltersSpy).toHaveBeenCalledWith(
        mockCategoryId,
        expectedCheckedValues
      );
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    let createCheckBoxItemSpy;

    beforeAll(() => {
      ({ props, wrapper } = setup());
      createCheckBoxItemSpy = jest.spyOn(
        wrapper.instance(),
        'createCheckBoxItem'
      );
      wrapper.instance().render();
    });
    it('calls createCheckBoxItem with correct parameters for each props.checkboxProperties', () => {
      props.checkboxProperties.forEach((item, index) => {
        expect(createCheckBoxItemSpy).toHaveBeenCalledWith(
          props.categoryId,
          `item:${props.categoryId}:${index}`,
          item
        );
      });
    });
  });

  describe('mapStateToProps', () => {
    const mockCategoryId = 'database';
    const { props } = setup({ categoryId: mockCategoryId });
    const mockFilters = { value: 'hive' };

    const mockStateWithFilters: GlobalState = {
      ...globalState,
      search: {
        ...globalState.search,
        resource: ResourceType.table,
        filters: {
          [ResourceType.table]: {
            [mockCategoryId]: mockFilters,
          },
        },
      },
    };

    const mockStateWithOutFilters: GlobalState = {
      ...globalState,
      search: {
        ...globalState.search,
        resource: ResourceType.user,
        filters: {
          [ResourceType.table]: {},
        },
      },
    };

    let result;
    beforeEach(() => {
      result = mapStateToProps(mockStateWithFilters, props);
    });

    it('sets checkedValues on the props with the filter value for the categoryId', () => {
      expect(result.checkedValues).toEqual(mockFilters.value.split(','));
    });

    it('sets checkedValues to empty object if no filters exist for the given resource', () => {
      result = mapStateToProps(mockStateWithOutFilters, props);
      expect(result.checkedValues).toEqual([]);
    });

    it('sets checkedValues to empty object if no filters exist for the given category', () => {
      const { props: fakeCategoryProps } = setup({
        categoryId: 'fakeCategory',
      });
      result = mapStateToProps(mockStateWithFilters, fakeCategoryProps);
      expect(result.checkedValues).toEqual([]);
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
  });
});
