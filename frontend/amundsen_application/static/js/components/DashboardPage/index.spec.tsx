import * as React from 'react';
import * as History from 'history';

import { shallow } from 'enzyme';

import { DashboardPage, DashboardPageProps, RouteProps } from './';
import { getMockRouterProps } from '../../fixtures/mockRouter';
import AvatarLabel from 'components/common/AvatarLabel';
import LoadingSpinner from 'components/common/LoadingSpinner';
import Breadcrumb from 'components/common/Breadcrumb';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import Flag from 'components/common/Flag';
import ResourceList from 'components/common/ResourceList';
import TabsComponent from 'components/common/TabsComponent';
import ChartList from './ChartList';
import ImagePreview from './ImagePreview';

import * as Constants from './constants';

import * as ConfigUtils from 'config/config-utils';
import { dashboardMetadata } from 'fixtures/metadata/dashboard';
import * as LogUtils from 'utils/logUtils';

import { ResourceType } from 'interfaces';

const MOCK_DISPLAY_NAME = 'displayName';
const MOCK_ICON_CLASS = 'dashboard-icon';

jest.mock('config/config-utils', () => (
  {
    getSourceDisplayName: jest.fn(() => { return MOCK_DISPLAY_NAME }),
    getSourceIconClass: jest.fn(() => { return MOCK_ICON_CLASS }),
  }
));

describe('DashboardPage', () => {
  const setStateSpy = jest.spyOn(DashboardPage.prototype, 'setState');
  const setup = (propOverrides?: Partial<DashboardPageProps>, location?: Partial<History.Location>) => {
    const routerProps = getMockRouterProps<RouteProps>(null, location);
    const props = {
      isLoading: false,
      statusCode: 200,
      dashboard: dashboardMetadata,
      getDashboard: jest.fn(),
      ...routerProps,
      ...propOverrides,
    };

    const wrapper = shallow<DashboardPage>(<DashboardPage {...props} />)
    return { props, wrapper };
  };

  describe('componentDidMount', () => {
    it('calls loadDashboard with uri from state', () => {
      const wrapper = setup().wrapper;
      const loadDashboardSpy = jest.spyOn(wrapper.instance(), 'loadDashboard');
      wrapper.instance().componentDidMount();
      expect(loadDashboardSpy).toHaveBeenCalledWith(wrapper.state().uri);
    });
  });

  describe('componentDidUpdate', () => {
    let props;
    let wrapper;
    let loadDashboardSpy;

    beforeEach(() => {
      const setupResult = setup(null, {
        search: '/dashboard?uri=testUri',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      loadDashboardSpy = jest.spyOn(wrapper.instance(), 'loadDashboard');
    });

    it('calls loadDashboard when uri has changes', () => {
      loadDashboardSpy.mockClear();
      setStateSpy.mockClear();
      wrapper.setProps({ location: { search: '/dashboard?uri=newUri'}});
      expect(loadDashboardSpy).toHaveBeenCalledWith('newUri');
      expect(setStateSpy).toHaveBeenCalledWith({ uri: 'newUri'});
    });

    it('does not call loadDashboard when uri has not changed', () => {
      loadDashboardSpy.mockClear();
      setStateSpy.mockClear();
      wrapper.instance().componentDidUpdate();
      expect(loadDashboardSpy).not.toHaveBeenCalled();
      expect(setStateSpy).not.toHaveBeenCalled();
    });
  });


  describe('loadDashboard', () => {
    let getLoggingParamsSpy;
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      getLoggingParamsSpy = jest.spyOn(LogUtils, 'getLoggingParams');
      wrapper.instance().loadDashboard('testUri');
    })
    it('calls getLoggingParams', () => {
      expect(getLoggingParamsSpy).toHaveBeenCalledWith(props.location.search);
    });
    it('calls props.getDashboard', () => {
      expect(props.getDashboard).toHaveBeenCalled();
    });
  });

  describe('mapStatusToStyle', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper
    });
    it('returns success if status === LAST_RUN_SUCCEEDED', () => {
      expect(wrapper.instance().mapStatusToStyle(Constants.LAST_RUN_SUCCEEDED)).toBe('success');
    });
    it('returns danger if status !== LAST_RUN_SUCCEEDED', () => {
      expect(wrapper.instance().mapStatusToStyle('anythingelse')).toBe('danger');
    });
  });

  describe('render', () => {
    const { props, wrapper } = setup();

    it('renders the loading spinner when loading', () => {
      const { props, wrapper } = setup({ isLoading: true })
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
      it('with link to add description if none exists', () => {
        const wrapper = setup({
          dashboard: {
            ...dashboardMetadata,
            description: '',
          }
        }).wrapper;
        const link = wrapper.find('a.edit-link');
        expect(link.props().href).toBe(props.dashboard.url);
        expect(link.text()).toBe(`${Constants.ADD_DESC_TEXT} ${MOCK_DISPLAY_NAME}`);
      });
    });

    describe('renders owners', () => {
      it('with correct AvatarLabel if no owners exist', () => {
        const wrapper = setup({
          dashboard: {
            ...dashboardMetadata,
            owners: [],
          }
        }).wrapper;
        expect(wrapper.find(AvatarLabel).props().label).toBe(Constants.NO_OWNER_TEXT)
      });
    });

    it('renders a Flag for last run state', () => {
      const mapStatusToStyleSpy = jest.spyOn(wrapper.instance(), 'mapStatusToStyle').mockImplementationOnce(() => 'testStyle');
      wrapper.instance().forceUpdate();
      const element = wrapper.find('.last-run-state').find(Flag);
      expect(element.props().text).toBe(props.dashboard.last_run_state);
      expect(mapStatusToStyleSpy).toHaveBeenCalledWith(props.dashboard.last_run_state);
      expect(element.props().labelStyle).toBe('testStyle');
    })

    it('renders an ImagePreview with correct props', () => {
      expect(wrapper.find(ImagePreview).props().uri).toBe(wrapper.state().uri);
    })
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
      const wrapper = setup({
        dashboard: {
          ...dashboardMetadata,
          chart_names: [],
        }
      }).wrapper;
      const result = shallow(wrapper.instance().renderTabs());
      expect(result.find(ChartList).exists()).toBe(false);
    });
  });
});
