// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import { GlobalState } from 'ducks/rootReducer';

import globalState from 'fixtures/globalState';

import { ResourceType } from 'interfaces';
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
      value: 'schema_name',
      filterState: { dashboard: { name: 'name' }, table: { column: 'column' } },
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
      expect(setStateSpy).toHaveBeenCalledWith({ value: newProps.value });
    });

    it('sets the value state to empty string if the property has change and is not truthy', () => {
      setStateSpy.mockClear();
      const newProps = {
        ...props,
        value: '',
      };
      wrapper.setProps(newProps);
      expect(setStateSpy).toHaveBeenCalledWith({ value: '' });
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
      expect(setStateSpy).toHaveBeenCalledWith({ value: expectedValue });
    });

    it('updates the global filter state', () => {
      updateFilterStateSpy.mockClear();
      const mockValue = 'mockValue';
      const mockEvent = { target: { value: mockValue } };
      wrapper.instance().onInputChange(mockEvent);

      props.filterState[props.resourceType][props.categoryId] = mockValue;
      expect(updateFilterStateSpy).toHaveBeenCalledWith(props.filterState);
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

    it('renders and input text with correct properties', () => {
      element = wrapper.find('input');
      expect(element.props().name).toBe(props.categoryId);
      expect(element.props().onChange).toBe(wrapper.instance().onInputChange);
      expect(element.props().value).toBe(wrapper.state().value);
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
