// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { ToggleButton, ToggleButtonGroup } from 'react-bootstrap';
import { shallow } from 'enzyme';

import { FilterOperationType } from 'interfaces/Enums';
import FilterOperationSelector, { FilterOperationSelectorProps } from '.';

describe('FilterOperationSelector', () => {
  const setup = (propOverrides?: Partial<FilterOperationSelectorProps>) => {
    const props: FilterOperationSelectorProps = {
      filterOperation: FilterOperationType.OR,
      handleFilterOperationChange: jest.fn(),
      multiValueSelection: true,
      categoryId: 'schema',
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow<typeof FilterOperationSelector>(
      <FilterOperationSelector {...props} />
    );
    return {
      props,
      wrapper,
    };
  };

  describe('render', () => {
    let props;
    let wrapper;
    let element;

    beforeAll(() => {
      ({ props, wrapper } = setup());
    });

    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();

      element = wrapper.find(ToggleButtonGroup);
      expect(element.props().onChange).toBe(props.handleFilterOperationChange);
      expect(element.props().value).toBe(props.filterOperation);
    });

    it('both filter operations enabled when it is a multivalue category', () => {
      ({ wrapper } = setup({ multiValueSelection: true }));
      expect(wrapper.find(ToggleButton).first().props().disabled).toBeFalsy();
      expect(wrapper.find(ToggleButton).at(1).props().disabled).toBeFalsy();
    });

    it('disables the AND operation when it is not a multivalue category', () => {
      ({ wrapper } = setup({ multiValueSelection: false }));
      expect(wrapper.find(ToggleButton).first().props().disabled).toBeTruthy();
      expect(wrapper.find(ToggleButton).at(1).props().disabled).toBeFalsy();
    });
  });
});
