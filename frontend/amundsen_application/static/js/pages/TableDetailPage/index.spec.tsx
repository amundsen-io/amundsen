// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as History from 'history';
import { shallow } from 'enzyme';

import { getMockRouterProps } from 'fixtures/mockRouter';
import { tableMetadata, tableLineage } from 'fixtures/metadata/table';

import LoadingSpinner from 'components/LoadingSpinner';
import TabsComponent from 'components/TabsComponent';

import * as ConfigUtils from 'config/config-utils';
import { TABLE_TAB } from './constants';
import { TableDetail, TableDetailProps, MatchProps } from '.';

const mockColumnDetails = {
  content: {
    title: 'column_name',
    description: 'description',
    nestedLevel: 0,
    hasStats: true,
  },
  type: { name: 'column_name', database: 'database', type: 'string' },
  usage: 0,
  stats: [
    {
      end_epoch: 1600473600,
      start_epoch: 1597881600,
      stat_type: 'column_usage',
      stat_val: '111',
    },
  ],
  children: [],
  action: { name: 'column_name', isActionEnabled: true },
  editText: 'Click to edit description in the data source site',
  editUrl: 'https://test.datasource.site/table',
  index: 0,
  key: 'database://cluster.schema/table/column_name',
  name: 'column_name',
  tableParams: {
    database: 'database',
    cluster: 'cluster',
    schema: 'schema',
    table: 'table',
  },
  sort_order: 0,
  isEditable: true,
  isExpandable: false,
  badges: [
    {
      badge_name: 'Badge Name 1',
      category: 'column',
    },
  ],
  typeMetadata: {
    kind: 'scalar',
    name: 'column_name',
    key: 'database://cluster.schema/table/column_name/type/column_name',
    description: 'description',
    data_type: 'string',
    sort_order: 0,
    is_editable: true,
  },
};

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
    tableLineage,
    isLoading: false,
    isLoadingDashboards: false,
    numRelatedDashboards: 0,
    statusCode: 200,
    tableData: tableMetadata,
    getTableData: jest.fn(),
    getTableLineageDispatch: jest.fn(),
    getColumnLineageDispatch: jest.fn(),
    openRequestDescriptionDialog: jest.fn(),
    searchSchema: jest.fn(),
    ...routerProps,
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = shallow<TableDetail>(<TableDetail {...props} />);

  return { props, wrapper };
};

describe('TableDetail', () => {
  describe('renderTabs', () => {
    let wrapper;
    beforeAll(() => {
      ({ wrapper } = setup());
    });
    it('does not render dashboard tab when disabled', () => {
      jest
        .spyOn(ConfigUtils, 'indexDashboardsEnabled')
        .mockImplementation(() => false);
      const content = shallow(<div>{wrapper.instance().renderTabs()}</div>);
      const tabInfo = content.find(TabsComponent).props().tabs;
      expect(
        tabInfo.find((tab) => tab.key === TABLE_TAB.DASHBOARD)
      ).toBeFalsy();
    });

    it('renders two tabs when dashboards are enabled', () => {
      jest
        .spyOn(ConfigUtils, 'indexDashboardsEnabled')
        .mockImplementation(() => true);
      const content = shallow(<div>{wrapper.instance().renderTabs()}</div>);
      const tabInfo = content.find(TabsComponent).props().tabs;
      expect(
        tabInfo.find((tab) => tab.key === TABLE_TAB.DASHBOARD)
      ).toBeTruthy();
    });
    it('does not render upstream and downstream tabs when disabled', () => {
      jest
        .spyOn(ConfigUtils, 'isTableListLineageEnabled')
        .mockImplementation(() => false);
      const content = shallow(<div>{wrapper.instance().renderTabs()}</div>);
      const tabInfo = content.find(TabsComponent).props().tabs;
      expect(tabInfo.find((tab) => tab.key === TABLE_TAB.UPSTREAM)).toBeFalsy();
      expect(
        tabInfo.find((tab) => tab.key === TABLE_TAB.DOWNSTREAM)
      ).toBeFalsy();
    });
    it('renders upstream and downstream tabs when enabled', () => {
      jest
        .spyOn(ConfigUtils, 'isTableListLineageEnabled')
        .mockImplementation(() => true);
      const content = shallow(<div>{wrapper.instance().renderTabs()}</div>);
      const tabInfo = content.find(TabsComponent).props().tabs;
      expect(
        tabInfo.find((tab) => tab.key === TABLE_TAB.UPSTREAM)
      ).toBeTruthy();
      expect(
        tabInfo.find((tab) => tab.key === TABLE_TAB.DOWNSTREAM)
      ).toBeTruthy();
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
    const setStateSpy = jest.spyOn(TableDetail.prototype, 'setState');
    describe('when mounted', () => {
      it('calls loadDashboard with uri from state', () => {
        const { props } = setup();
        const expected = 1;
        const actual = (props.getTableData as jest.Mock).mock.calls.length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when preExpandRightPanel is called when a column is preselected', () => {
      it('column lineage is populated and selected column details are set in the state', () => {
        setStateSpy.mockClear();
        const { props, wrapper } = setup();
        wrapper.instance().preExpandRightPanel(mockColumnDetails);

        expect(props.getColumnLineageDispatch).toHaveBeenCalled();
        expect(setStateSpy).toHaveBeenCalledWith({
          isRightPanelPreExpanded: true,
          isRightPanelOpen: true,
          selectedColumnKey: 'database://cluster.schema/table/column_name',
          selectedColumnDetails: mockColumnDetails,
        });
      });
    });

    describe('when toggleRightPanel is called while the panel is closed', () => {
      it('column lineage is populated and selected column details are set in the state', () => {
        setStateSpy.mockClear();
        const { props, wrapper } = setup();
        wrapper.setState({ isRightPanelOpen: false });
        wrapper.instance().toggleRightPanel(mockColumnDetails);

        expect(props.getColumnLineageDispatch).toHaveBeenCalled();
        expect(setStateSpy).toHaveBeenCalledWith({
          isRightPanelOpen: true,
          selectedColumnKey: 'database://cluster.schema/table/column_name',
          selectedColumnDetails: mockColumnDetails,
        });
      });
    });

    describe('when toggleRightPanel is called while the panel is open', () => {
      it('the panel is closed and the column details state is cleared', () => {
        setStateSpy.mockClear();
        const { wrapper } = setup();
        wrapper.setState({ isRightPanelOpen: true });
        wrapper.instance().toggleRightPanel(undefined);

        expect(setStateSpy).toHaveBeenCalledWith({
          isRightPanelOpen: false,
          selectedColumnKey: '',
          selectedColumnDetails: undefined,
        });
      });
    });

    describe('when toggleExpandingColumns is called while the columns are expanded', () => {
      it('toggles the areNestedColumnsExpanded state to false', () => {
        setStateSpy.mockClear();
        const { wrapper } = setup();
        wrapper.instance().toggleExpandingColumns();

        expect(setStateSpy).toHaveBeenCalledWith({
          areNestedColumnsExpanded: false,
        });
      });

      describe('when toggleExpandingColumns is called again after collapsing the columns', () => {
        it('toggles the areNestedColumnsExpanded state to true', () => {
          setStateSpy.mockClear();
          const { wrapper } = setup();
          wrapper.instance().toggleExpandingColumns();
          wrapper.instance().toggleExpandingColumns();

          expect(setStateSpy).toHaveBeenCalledWith({
            areNestedColumnsExpanded: true,
          });
        });
      });
    });
  });
});
