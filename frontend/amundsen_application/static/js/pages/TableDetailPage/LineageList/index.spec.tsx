// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import { LineageList, LineageListProps } from './index';

const setup = (propOverrides?: Partial<LineageListProps>) => {
  const props = {
    items: [],
    direction: 'upstream',
    ...propOverrides,
  };
  const wrapper = shallow(<LineageList {...props} />);

  return { props, wrapper };
};

describe('LineageList', () => {
  describe('render', () => {
    it('should render without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    it('should render a link', () => {
      const { wrapper } = setup({
        items: [
          {
            badges: [],
            cluster: 'gold',
            database: 'hive',
            key: 'hive://gold.test_schema/test_table1',
            level: 0,
            name: 'test_table1',
            parent: null,
            schema: 'test_schema',
            source: 'hive',
            usage: 0,
          },
        ],
        direction: 'both',
      });

      expect(wrapper.find('a').exists).toBeTruthy();
    });

    it('should have a disabled link', () => {
      jest.mock('./index', () => ({
        isTableLinkDisabled: jest.fn().mockReturnValueOnce(true),
      }));

      const { wrapper } = setup({
        items: [
          {
            badges: [],
            cluster: 'gold',
            database: 'hive',
            key: 'hive://gold.test_schema/test_table1',
            level: 0,
            name: 'test_table1',
            parent: null,
            schema: 'test_schema',
            source: 'hive',
            usage: 0,
          },
        ],
        direction: 'both',
      });

      expect(wrapper.find('is-disabled').exists).toBeTruthy();
    });

    describe('when no elements are passed', () => {
      it('should show an empty message', () => {
        const expected = 1;
        const { wrapper } = setup({});
        const actual = wrapper.find('.empty-message').length;

        expect(actual).toBe(expected);
      });
    });
  });
});
