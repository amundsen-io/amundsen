// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { mocked } from 'ts-jest/utils';
import { shallow } from 'enzyme';

import { ResourceType } from 'interfaces/Resources';
import {
  getSourceDisplayName,
  getDisplayNameByResource,
} from 'config/config-utils';
import TableHeaderBullets, { TableHeaderBulletsProps } from '.';

const MOCK_RESOURCE_DISPLAY_NAME = 'Test';
const MOCK_DB_DISPLAY_NAME = 'AlsoTest';
const TABLE_VIEW_TEXT = 'table view';

jest.mock('config/config-utils', () => ({
  getDisplayNameByResource: jest.fn(),
  getSourceDisplayName: jest.fn(),
}));

describe('TableHeaderBullets', () => {
  const setup = (propOverrides?: Partial<TableHeaderBulletsProps>) => {
    const props: TableHeaderBulletsProps = {
      database: 'hive',
      cluster: 'main',
      isView: true,
      ...propOverrides,
    };
    const wrapper = shallow(<TableHeaderBullets {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    let props: TableHeaderBulletsProps;
    let wrapper;
    let listElement;
    beforeAll(() => {
      mocked(getSourceDisplayName).mockImplementation(
        () => MOCK_DB_DISPLAY_NAME
      );
      mocked(getDisplayNameByResource).mockImplementation(
        () => MOCK_RESOURCE_DISPLAY_NAME
      );
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      listElement = wrapper.find('ul');
    });

    it('renders a list with correct class', () => {
      expect(listElement.props().className).toEqual('header-bullets');
    });

    it('renders a list with resource display name', () => {
      expect(getDisplayNameByResource).toHaveBeenCalledWith(ResourceType.table);
      expect(listElement.find('li').at(0).text()).toEqual(
        MOCK_RESOURCE_DISPLAY_NAME
      );
    });

    it('renders a list with database display name', () => {
      expect(getSourceDisplayName).toHaveBeenCalledWith(
        props.database,
        ResourceType.table
      );
      expect(listElement.find('li').at(1).text()).toEqual(MOCK_DB_DISPLAY_NAME);
    });

    it('renders a list with cluster', () => {
      expect(listElement.find('li').at(2).text()).toEqual(props.cluster);
    });

    it('renders a list with table view', () => {
      expect(listElement.find('li').at(3).text()).toEqual(TABLE_VIEW_TEXT);
    });
  });
});
