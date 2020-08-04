// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as ReactMarkdown from 'react-markdown';
import * as History from 'history';

import { shallow } from 'enzyme';

import AvatarLabel from 'components/common/AvatarLabel';
import LoadingSpinner from 'components/common/LoadingSpinner';
import Breadcrumb from 'components/common/Breadcrumb';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import Flag from 'components/common/Flag';
import ResourceList from 'components/common/ResourceList';
import TabsComponent from 'components/common/TabsComponent';
import { dashboardMetadata } from 'fixtures/metadata/dashboard';
import { NO_TIMESTAMP_TEXT } from 'components/constants';
import * as LogUtils from 'utils/logUtils';
import { ResourceType } from 'interfaces';
import { BadgeStyle } from 'config/config-types';
import ChartList from './ChartList';
import ImagePreview from './ImagePreview';

import { DashboardPage, DashboardPageProps, MatchProps } from '.';

import { getMockRouterProps } from '../../fixtures/mockRouter';

import * as Constants from './constants';

const MOCK_DISPLAY_NAME = 'displayName';
const MOCK_ICON_CLASS = 'dashboard-icon';

jest.mock('config/config-utils', () => ({
  getSourceDisplayName: jest.fn(() => {
    return MOCK_DISPLAY_NAME;
  }),
  getSourceIconClass: jest.fn(() => {
    return MOCK_ICON_CLASS;
  }),
}));
const setStateSpy = jest.spyOn(DashboardPage.prototype, 'setState');

const TEST_CLUSTER = 'gold';
const TEST_PRODUCT = 'mode';
const TEST_GROUP = '234testGroupID';
const TEST_DASHBOARD = '123DashboardID';

const setup = (
  propOverrides?: Partial<DashboardPageProps>,
  location?: Partial<History.Location>
) => {
  const routerProps = getMockRouterProps<MatchProps>(
    {
      uri: 'mode_dashboard://gold.234testGroupID/123DashboardID',
    },
    location
  );
  const props = {
    isLoading: false,
    statusCode: 200,
    dashboard: dashboardMetadata,
    getDashboard: jest.fn(),
    ...routerProps,
    ...propOverrides,
  };
  const wrapper = shallow<DashboardPage>(<DashboardPage {...props} />);

  return { props, wrapper };
};

describe('DashboardPage', () => {
  describe('componentDidMount', () => {
    it('calls getDashboard', () => {
      const { props, wrapper } = setup();

      wrapper.instance().componentDidMount();

      expect(props.getDashboard).toHaveBeenCalled();
    });

    it('calls getDashboard with the right parameters', () => {
      const { props, wrapper } = setup();
      const expectedURI = `${TEST_PRODUCT}_dashboard://${TEST_CLUSTER}.${TEST_GROUP}/${TEST_DASHBOARD}`;
      const expectedArguments = {
        source: undefined,
        searchIndex: undefined,
        uri: expectedURI,
      };

      wrapper.instance().componentDidMount();

      expect(props.getDashboard).toHaveBeenCalledWith(expectedArguments);
    });
  });

  describe('componentDidUpdate', () => {
    let props;
    let wrapper;
    let getDashboardSpy;

    beforeEach(() => {
      ({ props, wrapper } = setup());

      getDashboardSpy = props.getDashboard;
    });

    describe('when params change', () => {
      it('calls getDashboard', () => {
        getDashboardSpy.mockClear();
        setStateSpy.mockClear();
        const newParams = {
          uri:
            'testProduct_dashboard://testCluster.testGroupID/testDashboardID',
        };
        const expectedURI = `testProduct_dashboard://testCluster.testGroupID/testDashboardID`;
        const expectedArguments = {
          searchIndex: undefined,
          source: undefined,
          uri: expectedURI,
        };

        wrapper.setProps({ match: { params: newParams } });

        expect(getDashboardSpy).toHaveBeenCalledWith(expectedArguments);
        expect(setStateSpy).toHaveBeenCalledWith({ uri: expectedURI });
      });
    });

    describe('when params do not change', () => {
      it('does not call getDashboard', () => {
        getDashboardSpy.mockClear();
        setStateSpy.mockClear();

        wrapper.instance().componentDidUpdate();

        expect(getDashboardSpy).not.toHaveBeenCalled();
        expect(setStateSpy).not.toHaveBeenCalled();
      });
    });
  });

  describe('mapStatusToStyle', () => {
    let wrapper;

    beforeAll(() => {
      ({ wrapper } = setup());
    });

    it('returns BadgeStyle.SUCCESS if status === LAST_RUN_SUCCEEDED', () => {
      expect(
        wrapper.instance().mapStatusToStyle(Constants.LAST_RUN_SUCCEEDED)
      ).toBe(BadgeStyle.SUCCESS);
    });

    it('returns BadgeStyle.DANGER if status !== LAST_RUN_SUCCEEDED', () => {
      expect(wrapper.instance().mapStatusToStyle('anythingelse')).toBe(
        BadgeStyle.DANGER
      );
    });
  });

  describe('render', () => {
    const { props, wrapper } = setup();

    it('renders the loading spinner when loading', () => {
      const { wrapper } = setup({ isLoading: true });

      expect(wrapper.find(LoadingSpinner).exists()).toBeTruthy();
    });

    it('renders a breadcrumb component', () => {
      expect(wrapper.find(Breadcrumb).exists()).toBeTruthy();
    });

    it('renders a the dashboard title', () => {
      const headerText = wrapper.find('.header-title-text').text();

      expect(headerText).toEqual(props.dashboard.name);
    });

    it('renders a bookmark icon with correct props', () => {
      const elementProps = wrapper.find(BookmarkIcon).props();

      expect(elementProps.bookmarkKey).toBe(props.dashboard.uri);
      expect(elementProps.resourceType).toBe(ResourceType.dashboard);
    });

    describe('renders description', () => {
      it('using a ReactMarkdown component', () => {
        const markdown = wrapper.find(ReactMarkdown);
        expect(markdown.exists()).toBe(true);
        expect(markdown.props()).toMatchObject({
          source: props.dashboard.description,
        });
      });

      it('with link to add description if none exists', () => {
        const { wrapper } = setup({
          dashboard: {
            ...dashboardMetadata,
            description: '',
          },
        });
        const link = wrapper.find('a.edit-link');

        expect(link.props().href).toBe(props.dashboard.url);
        expect(link.text()).toBe(
          `${Constants.ADD_DESC_TEXT} ${MOCK_DISPLAY_NAME}`
        );
      });
    });

    describe('renders owners', () => {
      it('with correct AvatarLabel if no owners exist', () => {
        const { wrapper } = setup({
          dashboard: {
            ...dashboardMetadata,
            owners: [],
          },
        });

        expect(wrapper.find(AvatarLabel).props().label).toBe(
          Constants.NO_OWNER_TEXT
        );
      });
    });

    it('renders a Flag for last run state', () => {
      const mockStyle = BadgeStyle.DANGER;
      const mapStatusToStyleSpy = jest
        .spyOn(wrapper.instance(), 'mapStatusToStyle')
        .mockImplementationOnce(() => mockStyle);
      wrapper.instance().forceUpdate();
      const element = wrapper.find('.last-run-state').find(Flag);

      expect(element.props().text).toBe(props.dashboard.last_run_state);
      expect(mapStatusToStyleSpy).toHaveBeenCalledWith(
        props.dashboard.last_run_state
      );
      expect(element.props().labelStyle).toBe(mockStyle);
    });

    it('renders an ImagePreview with correct props', () => {
      expect(wrapper.find(ImagePreview).props().uri).toBe(wrapper.state().uri);
    });

    describe('renders timestamps correctly when unavailable', () => {
      const { wrapper } = setup({
        dashboard: {
          ...dashboardMetadata,
          last_run_timestamp: null,
          last_successful_run_timestamp: null,
        },
      });

      it('last_run_timestamp', () => {
        expect(wrapper.find('.last-run-timestamp').text()).toEqual(
          NO_TIMESTAMP_TEXT
        );
      });

      it('last_successful_run_timestamp', () => {
        expect(wrapper.find('.last-successful-run-timestamp').text()).toEqual(
          NO_TIMESTAMP_TEXT
        );
      });
    });
  });

  describe('renderTabs', () => {
    const { props, wrapper } = setup();

    it('returns a ResourceList', () => {
      const result = shallow(wrapper.instance().renderTabs());
      const element = result.find(ResourceList);

      expect(element.exists()).toBe(true);
      expect(element.props().allItems).toEqual(props.dashboard.tables);
    });

    it('returns a Tabs component', () => {
      const result = wrapper.instance().renderTabs();

      expect(result.type).toEqual(TabsComponent);
    });

    it('does not render ChartList if no charts', () => {
      const { wrapper } = setup({
        dashboard: {
          ...dashboardMetadata,
          chart_names: [],
        },
      });
      const result = shallow(wrapper.instance().renderTabs());

      expect(result.find(ChartList).exists()).toBe(false);
    });
  });
});
