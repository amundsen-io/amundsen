// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';
import LineageList, { LineageListProps } from './index';

const setup = (propOverrides?: Partial<LineageListProps>) => {
  const props: LineageListProps = {
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
    ...propOverrides,
  };
  const wrapper = shallow<typeof LineageList>(<LineageList {...props} />);

  return {
    props,
    wrapper,
  };
};

describe('LineageList', () => {
  it('should render a link', () => {
    const { wrapper } = setup();
    expect(wrapper.find('a').exists).toBeTruthy();
  });

  it('should have a disabled link', () => {
    const { wrapper } = setup();
    jest.mock('./index', () => ({
      isTableLinkDisabled: jest.fn().mockReturnValueOnce(true),
    }));
    expect(wrapper.find('is-disabled').exists).toBeTruthy();
  });
});
