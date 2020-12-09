// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as History from 'history';
import { mount, shallow } from 'enzyme';
import { mocked } from 'ts-jest/utils';

import { getMockRouterProps } from 'fixtures/mockRouter';
import { tableMetadata } from 'fixtures/metadata/table';

import LoadingSpinner from 'components/LoadingSpinner';
import TabsComponent from 'components/TabsComponent';

import { indexDashboardsEnabled } from 'config/config-utils';
import { TableDetail, TableDetailProps, MatchProps } from '.';

jest.mock('config/config-utils', () => ({
  indexDashboardsEnabled: jest.fn(),
  getTableSortCriterias: jest.fn(),
}));

const setup = (
  propOverrides?: Partial<TableDetailProps>,
  location?: Partial<History.Location>
) => {
  const routerProps = getMockRouterProps<MatchProps>(
    {
      cluster: 'gold',
      database: 'hive',
      schema: 'base',
      table: 'rides',
    },
    location
  );
  const props = {
    isLoading: false,
    isLoadingDashboards: false,
    numRelatedDashboards: 0,
    statusCode: 200,
    tableData: tableMetadata,
    getTableData: jest.fn(),
    openRequestDescriptionDialog: jest.fn(),
    searchSchema: jest.fn(),
    ...routerProps,
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = mount<TableDetail>(<TableDetail {...props} />);

  return { props, wrapper };
};

describe('TableDetail', () => {
  describe('renderTabs', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper;
    });
    it('renders one tab when dashboards are not enabled', () => {
      mocked(indexDashboardsEnabled).mockImplementation(() => false);
      const content = shallow(<div>{wrapper.instance().renderTabs()}</div>);
      expect(content.find(TabsComponent).props().tabs.length).toEqual(1);
    });

    it('renders two tabs when dashboards are enabled', () => {
      mocked(indexDashboardsEnabled).mockImplementation(() => true);
      const content = shallow(<div>{wrapper.instance().renderTabs()}</div>);
      expect(content.find(TabsComponent).props().tabs.length).toEqual(2);
    });
  });

  describe('render', () => {
    it('should render without problems', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    it('should render the Loading Spinner', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find(LoadingSpinner).length;

      expect(actual).toEqual(expected);
    });
  });

  describe('lifecycle', () => {
    describe('when mounted', () => {
      it('calls loadDashboard with uri from state', () => {
        const { props } = setup();
        const expected = 1;
        const actual = (props.getTableData as jest.Mock).mock.calls.length;

        expect(actual).toEqual(expected);
      });
    });
  });
});
