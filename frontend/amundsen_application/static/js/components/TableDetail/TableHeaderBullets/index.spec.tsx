import * as React from 'react';

import { mocked } from 'ts-jest/utils';
import { shallow } from 'enzyme';

import TableHeaderBullets, { TableHeaderBulletsProps } from '.';

import { ResourceType } from 'interfaces/Resources';

const MOCK_RESOURCE_DISPLAY_NAME = 'Test';
const MOCK_DB_DISPLAY_NAME = 'AlsoTest';

jest.mock('config/config-utils', () => ({
  getDisplayNameByResource: jest.fn(),
  getSourceDisplayName: jest.fn()
}));
import { getSourceDisplayName, getDisplayNameByResource } from 'config/config-utils';

describe('TableHeaderBullets', () => {
  const setup = (propOverrides?: Partial<TableHeaderBulletsProps>) => {
    const props: TableHeaderBulletsProps = {
      database: 'hive',
      cluster: 'main',
      ...propOverrides
    };
    const wrapper = shallow(<TableHeaderBullets {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    let props: TableHeaderBulletsProps;
    let wrapper;
    let listElement;
    beforeAll(() => {
      mocked(getSourceDisplayName).mockImplementation(() => MOCK_DB_DISPLAY_NAME);
      mocked(getDisplayNameByResource).mockImplementation(() => MOCK_RESOURCE_DISPLAY_NAME);
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
      expect(listElement.find('li').at(0).text()).toEqual(MOCK_RESOURCE_DISPLAY_NAME);
    });

    it('renders a list with database display name', () => {
      expect(getSourceDisplayName).toHaveBeenCalledWith(props.database, ResourceType.table);
      expect(listElement.find('li').at(1).text()).toEqual(MOCK_DB_DISPLAY_NAME);
    });

    it('renders a list with cluster', () => {
      expect(listElement.find('li').at(2).text()).toEqual(props.cluster);
    });
  });
});
