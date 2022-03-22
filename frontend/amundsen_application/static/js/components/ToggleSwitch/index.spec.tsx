// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { mount } from 'enzyme';

import Switch from 'react-switch';
import ToggleSwitch, { ToggleSwitchProps } from './ToggleSwitch';

const setup = (propOverrides?: Partial<ToggleSwitchProps>) => {
  const props: ToggleSwitchProps = {
    checked: true,
    onChange: jest.fn(),
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = mount(<ToggleSwitch {...props} />);

  return {
    props,
    wrapper,
  };
};

describe('ToggleSwitch', () => {
  describe('render', () => {
    it('renders the switch component', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find(Switch).length;
      expect(actual).toEqual(expected);
    });
    it('renders the switch with correct state', () => {
      const { wrapper } = setup();
      const expected = true;
      const actual = wrapper.find('input').props()['aria-checked'];
      expect(actual).toEqual(expected);
    });
  });
});
