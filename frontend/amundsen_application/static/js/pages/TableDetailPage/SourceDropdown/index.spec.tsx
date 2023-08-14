// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { mount } from 'enzyme';

import SourceDropdown, { SourceDropdownProps } from '.';


const setup = (propOverrides?: Partial<SourceDropdownProps>) => {
  const props = {
    tableSources: [{
      source_type: 'xyz',
      source: 'www.xyz.com',
    }],
    ...propOverrides,
  };
  const wrapper = mount<typeof SourceDropdown>(
    <SourceDropdown {...props} />
  );

  return { props, wrapper };
};

describe('SourceDropdown', () => {
  describe('render', () => {
    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    describe('when no options are passed', () => {
      it('does not render the component', () => {
        const { wrapper } = setup();
        const expected = 0;
        const actual = wrapper.find('.source-dropdown').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when one option is passed', () => {
      it('renders a Dropdown component', () => {
        const { wrapper } = setup({
          tableSources: [{
            source_type: 'xyz',
            source: 'www.xyz.com',
          }],
        });
        const expected = 1;
        const actual = wrapper.find(Dropdown).length;

        expect(actual).toEqual(expected);
      });

      it('renders a MenuItem component', () => {
        const { wrapper } = setup({
          tableSources: [{
            source_type: 'xyz',
            source: 'www.xyz.com',
          }],
        });
        const expected = 1;
        const actual = wrapper.find(MenuItem).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when two options are passed', () => {
      it('renders a Dropdown component', () => {
        const { wrapper } = setup({
          tableSources: [{
            source_type: 'xyz',
            source: 'www.xyz.com',
          }],
        });
        const expected = 1;
        const actual = wrapper.find(Dropdown).length;

        expect(actual).toEqual(expected);
      });

      it('renders two MenuItem components and a MenuItem divider between kinds', () => {
        const { wrapper } = setup({
          tableSources: [{
            source_type: 'xyz',
            source: 'www.xyz.com',
          }],
        });
        const expected = 3;
        const actual = wrapper.find(MenuItem).length;

        expect(actual).toEqual(expected);
      });      
    });
  });
});
