// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { OverlayTrigger, Popover } from 'react-bootstrap';
import SanitizedHTML from 'react-sanitized-html';
import { shallow } from 'enzyme';

import { GlobalState } from 'ducks/rootReducer';

import globalState from 'fixtures/globalState';

import { FilterOperationType, ResourceType } from 'interfaces';
import FilterOperationSelector from '../FilterOperationSelector';
import {
  InputFilter,
  InputFilterProps,
  mapDispatchToProps,
  mapStateToProps,
} from '.';

describe('InputFilter', () => {
  const setStateSpy = jest.spyOn(InputFilter.prototype, 'setState');

  const setup = (propOverrides?: Partial<InputFilterProps>) => {
    const props: InputFilterProps = {
      categoryId: 'schema',
      allowableOperation: FilterOperationType.OR,
      value: 'schema_name',
      filterOperation: FilterOperationType.OR,
      filterState: {
        dashboard: { name: { value: 'name' } },
        table: { column: { value: 'column' } },
      },
      resourceType: ResourceType.table,
      updateFilterState: jest.fn(),
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow<InputFilter>(<InputFilter {...props} />);
    return {
      props,
      wrapper,
    };
  };

  describe('constructor', () => {
    const testValue = 'test';
    let wrapper;
    beforeAll(() => {
      ({ wrapper } = setup({ value: testValue }));
    });
    it('sets the value state from props', () => {
      expect(wrapper.state().value).toEqual(testValue);
    });
  });

  describe('componentDidUpdate', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      ({ props, wrapper } = setup());
    });
    it('sets the value state to props.value if the property has changed', () => {
      setStateSpy.mockClear();
      const newProps = {
        ...props,
        value: 'Some new value',
      };
      wrapper.setProps(newProps);
      expect(setStateSpy).toHaveBeenCalledWith({
        value: newProps.value,
        showFilterOperationToggle: false,
        filterOperation: FilterOperationType.OR,
      });
    });

    it('sets the value state to empty string if the property has change and is not truthy', () => {
      setStateSpy.mockClear();
      const newProps = {
        ...props,
        value: '',
      };
      wrapper.setProps(newProps);
      expect(setStateSpy).toHaveBeenCalledWith({
        value: '',
        showFilterOperationToggle: false,
        filterOperation: FilterOperationType.OR,
      });
    });

    it('does not call set state if props.value has not changed', () => {
      wrapper.setProps(props);
      setStateSpy.mockClear();
      wrapper.setProps(props);
      expect(setStateSpy).not.toHaveBeenCalled();
    });
  });

  describe('onInputChange', () => {
    let props;
    let wrapper;
    let updateFilterStateSpy;
    beforeAll(() => {
      ({ props, wrapper } = setup());
      updateFilterStateSpy = jest.spyOn(props, 'updateFilterState');
    });
    it('sets the value state to e.target.value', () => {
      setStateSpy.mockClear();
      const mockValue = 'mockValue';
      const expectedValue = 'mockvalue';
      const mockEvent = { target: { value: mockValue } };
      wrapper.instance().onInputChange(mockEvent);
      expect(setStateSpy).toHaveBeenCalledWith({
        value: expectedValue,
        showFilterOperationToggle: false,
      });
    });

    it('shows the filter operation toggle', () => {
      setStateSpy.mockClear();
      const mockValue = 'mockValue1, mockValue2';
      const expectedValue = 'mockvalue1, mockvalue2';
      const mockEvent = { target: { value: mockValue } };
      wrapper.instance().onInputChange(mockEvent);
      expect(setStateSpy).toHaveBeenCalledWith({
        value: expectedValue,
        showFilterOperationToggle: true,
      });
    });

    it('updates the global filter state with the new value', () => {
      updateFilterStateSpy.mockClear();
      const mockValue = 'mockValue';
      const mockEvent = { target: { value: mockValue } };
      wrapper.instance().onInputChange(mockEvent);

      const newFilters = {
        ...props.filterState,
        [props.resourceType]: {
          ...props.filterState[props.resourceType],
          [props.categoryId]: { value: mockValue.toLowerCase() },
        },
      };
      expect(updateFilterStateSpy).toHaveBeenCalledWith(newFilters);
    });

    it('updates the global filter state including the existing filter operation', () => {
      ({ wrapper, props } = setup({
        filterState: {
          table: {
            schema: {
              value: 'schema1, schema2',
              filterOperation: FilterOperationType.AND,
            },
          },
        },
      }));
      updateFilterStateSpy = jest.spyOn(props, 'updateFilterState');
      updateFilterStateSpy.mockClear();
      const mockValue = 'mockValue1, mockValue2';
      const mockFilterOperation = FilterOperationType.AND;
      const mockEvent = { target: { value: mockValue } };
      wrapper.instance().onInputChange(mockEvent);

      const newFilters = {
        ...props.filterState,
        [props.resourceType]: {
          ...props.filterState[props.resourceType],
          [props.categoryId]: {
            value: mockValue.toLowerCase(),
            filterOperation: mockFilterOperation,
          },
        },
      };
      expect(updateFilterStateSpy).toHaveBeenCalledWith(newFilters);
    });
  });

  describe('handleFilterOperationChange', () => {
    let props;
    let wrapper;
    let updateFilterStateSpy;
    beforeAll(() => {
      ({ props, wrapper } = setup());
      updateFilterStateSpy = jest.spyOn(props, 'updateFilterState');
    });
    it('sets the filterOperation state to the new value', () => {
      setStateSpy.mockClear();
      const mockOperation = FilterOperationType.AND;
      wrapper.instance().handleFilterOperationChange(mockOperation);
      expect(setStateSpy).toHaveBeenCalledWith({
        filterOperation: mockOperation,
      });
    });

    it('updates the global filter state with the new filter operation', () => {
      updateFilterStateSpy.mockClear();
      const mockOperation = FilterOperationType.AND;
      wrapper.instance().handleFilterOperationChange(mockOperation);

      const newFilters = {
        ...props.filterState,
        [props.resourceType]: {
          ...props.filterState[props.resourceType],
          [props.categoryId]: { filterOperation: mockOperation },
        },
      };
      expect(updateFilterStateSpy).toHaveBeenCalledWith(newFilters);
    });

    it('updates the global filter state including the existing input value', () => {
      ({ wrapper, props } = setup({
        filterState: {
          table: {
            schema: {
              value: 'schema1, schema2',
              filterOperation: FilterOperationType.OR,
            },
          },
        },
      }));
      updateFilterStateSpy = jest.spyOn(props, 'updateFilterState');
      updateFilterStateSpy.mockClear();
      const mockValue = 'schema1, schema2';
      const mockOperation = FilterOperationType.AND;
      wrapper.instance().handleFilterOperationChange(mockOperation);

      const newFilters = {
        ...props.filterState,
        [props.resourceType]: {
          ...props.filterState[props.resourceType],
          [props.categoryId]: {
            value: mockValue.toLowerCase(),
            filterOperation: mockOperation,
          },
        },
      };
      expect(updateFilterStateSpy).toHaveBeenCalledWith(newFilters);
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    let element;

    beforeAll(() => {
      ({ props, wrapper } = setup());
      wrapper.instance().render();
    });

    it('renders an input text field with correct properties', () => {
      element = wrapper.find('input');
      expect(element.props().name).toBe(props.categoryId);
      expect(element.props().onChange).toBe(wrapper.instance().onInputChange);
      expect(element.props().value).toBe(wrapper.state().value);
    });

    it('does not render a filter operation selector', () => {
      wrapper.instance().setState({ showFilterOperationToggle: false });
      expect(wrapper.find(FilterOperationSelector).exists()).toBeFalsy();
    });

    it('renders a filter operation selector', () => {
      wrapper.instance().setState({ showFilterOperationToggle: true });
      expect(wrapper.find(FilterOperationSelector).exists()).toBeTruthy();
    });

    it('does not render an OverlayTrigger', () => {
      element = wrapper.find(OverlayTrigger);
      expect(element.exists()).toBeFalsy();
    });

    it('renders an OverlayTrigger with correct popover', () => {
      const mockHelpText = 'Help';
      const expectedPopover = (
        <Popover id="schema-help-text-popover">
          <SanitizedHTML html={mockHelpText} />
        </Popover>
      );

      ({ wrapper } = setup({ helpText: mockHelpText }));
      element = wrapper.find(OverlayTrigger);

      expect(element.exists()).toBeTruthy();
      expect(element.props().overlay).toEqual(expectedPopover);
    });
  });

  describe('mapStateToProps', () => {
    let props;
    const mockCategoryId = 'schema';
    ({ props } = setup({ categoryId: mockCategoryId }));
    const mockFilters = 'schema_name';

    const mockStateWithFilters: GlobalState = {
      ...globalState,
      search: {
        ...globalState.search,
        resource: ResourceType.table,
        filters: {
          [ResourceType.table]: {
            [mockCategoryId]: { value: mockFilters },
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

    it('sets value on the props with the filter value for the categoryId', () => {
      expect(result.value).toBe(mockFilters);
    });

    it('sets value to empty string if no filters exist for the given resource', () => {
      result = mapStateToProps(mockStateWithOutFilters, props);
      expect(result.value).toEqual('');
    });

    it('sets value to empty string if no filters exist for the given category', () => {
      ({ props } = setup({ categoryId: 'fakeCategory' }));
      result = mapStateToProps(mockStateWithFilters, props);
      expect(result.value).toEqual('');
    });
  });

  describe('mapDispatchToProps', () => {
    let dispatch;
    let result;
    beforeAll(() => {
      dispatch = jest.fn(() => Promise.resolve());
      result = mapDispatchToProps(dispatch);
    });

    it('sets updateFilterState on the props', () => {
      expect(result.updateFilterState).toBeInstanceOf(Function);
    });
  });
});
