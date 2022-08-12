// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';
import LineageList from './index';

describe('LineageList', () => {
  let wrapper;
  let props;
  beforeAll(() => {
    props = {
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
    };
    wrapper = shallow<typeof LineageList>(<LineageList {...props} />);
  });

  it('should render a link', () => {
    expect(wrapper.find('a').exists).toBeTruthy();
  });

  it('should have a disabled link', () => {
    jest.mock('./index', () => ({
      isTableLinkDisabled: jest.fn().mockReturnValueOnce(true),
    }));
    expect(wrapper.find('is-disabled').exists).toBeTruthy();
  });
});
