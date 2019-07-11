import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as History from 'history';

import { shallow } from 'enzyme';

import AppConfig from 'config/config';
import { ResourceType } from 'interfaces';
import { SearchPage, SearchPageProps, mapDispatchToProps, mapStateToProps } from '../';
import {
  DOCUMENT_TITLE_SUFFIX,
  PAGINATION_PAGE_RANGE,
  PAGE_INDEX_ERROR_MESSAGE,
  RESULTS_PER_PAGE,
  SEARCH_ERROR_MESSAGE_INFIX,
  SEARCH_ERROR_MESSAGE_PREFIX,
  SEARCH_ERROR_MESSAGE_SUFFIX,
  SEARCH_INFO_TEXT,
  SEARCH_SOURCE_NAME,
  TABLE_RESOURCE_TITLE,
} from '../constants';

import InfoButton from 'components/common/InfoButton';
import TabsComponent from 'components/common/Tabs';

import SearchBar from '../SearchBar';

import LoadingSpinner from 'components/common/LoadingSpinner';

import ResourceList from 'components/common/ResourceList';
import globalState from 'fixtures/globalState';
import { getMockRouterProps } from 'fixtures/mockRouter';

describe('SearchPage', () => {
  const setStateSpy = jest.spyOn(SearchPage.prototype, 'setState');
  const setup = (propOverrides?: Partial<SearchPageProps>, location?: Partial<History.Location>) => {
    const routerProps = getMockRouterProps<any>(null, location);
    const props: SearchPageProps = {
      searchTerm: globalState.search.search_term,
      isLoading: false,
      dashboards: globalState.search.dashboards,
      tables: globalState.search.tables,
      users: globalState.search.users,
      searchAll: jest.fn(),
      searchResource: jest.fn(),
      ...routerProps,
      ...propOverrides,
    };
    const wrapper = shallow<SearchPage>(<SearchPage {...props} />)
    return { props, wrapper };
  };

  describe('constructor', () => {
    it('sets the default selectedTab', () => {
      const { props, wrapper } = setup();
      expect(wrapper.state().selectedTab).toEqual(ResourceType.table);
    });
  });

  describe('componentDidMount', () => {
    let props;
    let wrapper;
    let mockSearchOptions;
    let mockSanitizedUrlParams;

    let createSearchOptionsSpy;
    let getSanitizedUrlParamsSpy;
    let searchAllSpy;
    let updatePageUrlSpy;

    beforeAll(() => {
      const setupResult = setup(null, {
        search: '/search?searchTerm=testName&selectedTab=table&pageIndex=1',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      mockSanitizedUrlParams = { 'term': 'testName', ' index': 1, 'currentTab': 'table' };
      getSanitizedUrlParamsSpy = jest.spyOn(wrapper.instance(), 'getSanitizedUrlParams').mockImplementation(() => {
        return mockSanitizedUrlParams;
      });
      mockSearchOptions = { 'dashboardIndex': 0, 'tableIndex': 0, 'userIndex': 1 };
      createSearchOptionsSpy = jest.spyOn(wrapper.instance(), 'createSearchOptions').mockImplementation(() => {
        return mockSearchOptions;
      });
      searchAllSpy = jest.spyOn(props, 'searchAll');
      updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
      setStateSpy.mockClear();

      wrapper.instance().componentDidMount();
    });

    it('calls setState', () => {
      expect(setStateSpy).toHaveBeenCalledWith({ selectedTab: mockSanitizedUrlParams.currentTab });
    });

    describe('when searchTerm in params is valid', () => {
      beforeAll(() => {
        updatePageUrlSpy.mockClear();
        const {props, wrapper} = setup(null, {
          search: '/search?searchTerm=testName&selectedTab=table&pageIndex=1',
        });
        updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
        wrapper.instance().componentDidMount();
      });
      it('calls searchAll', () => {
        expect(searchAllSpy).toHaveBeenCalledWith(mockSanitizedUrlParams.term, mockSearchOptions);
      });

      it('does not call updateURL', () => {
        expect(updatePageUrlSpy).not.toHaveBeenCalled();
      });
    });

    describe('when pageIndex in params is undefined', () => {
      let mockSanitizedUrlParams;
      let getSanitizedUrlParamsSpy;

      let updatePageUrlSpy;

      beforeAll(() => {
        const {props, wrapper} = setup(null, {
          search: '/search?searchTerm=testName',
        });
        mockSanitizedUrlParams = { 'term': 'testName', ' index': 0, 'currentTab': 'table' };
        getSanitizedUrlParamsSpy = jest.spyOn(wrapper.instance(), 'getSanitizedUrlParams').mockImplementation(() => {
          return mockSanitizedUrlParams;
        });
        updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
        wrapper.instance().componentDidMount();
      });
      it('uses 0 as pageIndex', () => {
        expect(updatePageUrlSpy).toHaveBeenCalledWith(mockSanitizedUrlParams.term, mockSanitizedUrlParams.currentTab, mockSanitizedUrlParams.index);
      });
    });

    describe('when searchTerm in params is undefined', () => {
      beforeAll(() => {
        searchAllSpy.mockClear();
        updatePageUrlSpy.mockClear();
        const {props, wrapper} = setup(null, {
          search: '/search?selectedTab=table&pageIndex=1',
        });
        updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
        wrapper.instance().componentDidMount();
      });
      it('does not call searchAll', () => {
        expect(searchAllSpy).not.toHaveBeenCalled();
      });

      it('does not call updatePageUrl', () => {
        expect(updatePageUrlSpy).not.toHaveBeenCalled();
      });
    });

    describe('when searchTerm in params is empty string', () => {
      beforeAll(() => {
        searchAllSpy.mockClear();
        updatePageUrlSpy.mockClear();
        const {props, wrapper} = setup(null, {
          search: '/search?searchTerm=&selectedTab=table&pageIndex=1',
        });
        updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
        wrapper.instance().componentDidMount();
      });
      it('does not call searchAll', () => {
        expect(searchAllSpy).not.toHaveBeenCalled();
      });

      it('does not call updatePageUrl', () => {
        expect(updatePageUrlSpy).not.toHaveBeenCalled();
      });
    });

    afterAll(() => {
      createSearchOptionsSpy.mockRestore();
    });
  });

  describe('componentDidUpdate', () => {
    let searchAllSpy;

    let mockSearchOptions;
    let mockSanitizedUrlParams;

    let createSearchOptionsSpy;
    let getSanitizedUrlParamsSpy;

    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup(null, {
        search: '/search?searchTerm=current&selectedTab=table&pageIndex=0',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      mockSanitizedUrlParams = { 'term': 'current', ' index': 0, 'currentTab': 'table' };
      getSanitizedUrlParamsSpy = jest.spyOn(wrapper.instance(), 'getSanitizedUrlParams').mockImplementation(() => {
        return mockSanitizedUrlParams;
      });

      mockSearchOptions = { 'dashboardIndex': 0, 'tableIndex': 1, 'userIndex': 0 };
      createSearchOptionsSpy = jest.spyOn(wrapper.instance(), 'createSearchOptions').mockImplementation(() => {
        return mockSearchOptions;
      });

      searchAllSpy = jest.spyOn(props, 'searchAll');

      setStateSpy.mockClear();

      const mockPrevProps = {
        searchTerm: 'previous',
        location: {
          search: '/search?searchTerm=previous&selectedTab=table&pageIndex=0',
          pathname: 'mockstr',
          state: jest.fn(),
          hash: 'mockstr',
        }
      };
      wrapper.instance().componentDidUpdate(mockPrevProps);
    });

    it('calls setState', () => {
      expect(setStateSpy).toHaveBeenCalledWith({ selectedTab: ResourceType.table });
    });

    it('calls searchAll if called with a new search term', () => {
      expect(searchAllSpy).toHaveBeenCalledWith(mockSanitizedUrlParams.term, mockSearchOptions);
    });

    it('does not call searchAll if called with the same search term with a new page', () => {
      searchAllSpy.mockClear();
      const mockPrevProps = {
        searchTerm: 'current',
        location: {
          search: '/search?searchTerm=current&current=table&pageIndex=1',
          pathname: 'mockstr',
          state: jest.fn(),
          hash: 'mockstr',
        }
      };
      wrapper.instance().componentDidUpdate(mockPrevProps);
      expect(searchAllSpy).not.toHaveBeenCalled();
    });
  });

  describe('getSanitizedUrlParams', () => {
    let props;
    let wrapper;
    let getSelectedTabByResourceTypeSpy;

    let mockSelectedTab;

    beforeAll(() => {
      const setupResult = setup(null, {
        search: '/search?searchTerm=current&selectedTab=table&pageIndex=0',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      const mockResourceType = ResourceType.table;
      getSelectedTabByResourceTypeSpy = jest.spyOn(wrapper.instance(), 'getSelectedTabByResourceType').mockImplementation(() => {
        return mockResourceType;
      });

      mockSelectedTab = ResourceType.table;

      wrapper.instance().getSanitizedUrlParams('current', 0, mockSelectedTab)
    });

    it('calls getSelectedTabByResourceType with correct value', () => {
      expect(getSelectedTabByResourceTypeSpy).toHaveBeenCalledWith(mockSelectedTab);
    });

    it('output of getSanitizedUrlParams is expected', () => {
      const expected = {'term': 'current', 'index': 0, 'currentTab': ResourceType.table};
      expect(wrapper.instance().getSanitizedUrlParams('current', 0, ResourceType.table)).toEqual(expected);
    });

    it('output of getSanitizedUrlParams is expected for undefined vars', () => {
      const expected = {'term': '', 'index': 0, 'currentTab': ResourceType.table};
      expect(wrapper.instance().getSanitizedUrlParams(undefined, undefined, ResourceType.table)).toEqual(expected);
    });
  });

  describe('getSelectedTabByResourceType', () => {
    let props;
    let wrapper;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('returns given tab if equal to ResourceType.table', () => {
      expect(wrapper.instance().getSelectedTabByResourceType(ResourceType.table)).toEqual(ResourceType.table);
    });

    it('returns given tab if equal to ResourceType.user', () => {
      expect(wrapper.instance().getSelectedTabByResourceType(ResourceType.user)).toEqual(ResourceType.user);
    });

    it('returns state.selectedTab if given equal to ResourceType.dashboard', () => {
      wrapper.setState({ selectedTab: 'user' })
      expect(wrapper.instance().getSelectedTabByResourceType(ResourceType.dashboard)).toEqual('user');
    });

    it('returns state.selectedTab in default case', () => {
      wrapper.setState({ selectedTab: 'table' })
      // @ts-ignore: cover default case
      expect(wrapper.instance().getSelectedTabByResourceType('not valid')).toEqual('table');
    });
  });

  describe('createSearchOptions', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('generates correct options if selectedTab === ResourceType.dashboard', () => {
      expect(wrapper.instance().createSearchOptions(5, ResourceType.dashboard)).toMatchObject({
        dashboardIndex: 5,
        userIndex: 0,
        tableIndex: 0,
      });
    });

    it('generates correct options if selectedTab === ResourceType.user', () => {
      expect(wrapper.instance().createSearchOptions(5, ResourceType.user)).toMatchObject({
        dashboardIndex: 0,
        userIndex: 5,
        tableIndex: 0,
      });
    });

    it('generates correct options if selectedTab === ResourceType.table', () => {
      expect(wrapper.instance().createSearchOptions(5, ResourceType.table)).toMatchObject({
        dashboardIndex: 0,
        userIndex: 0,
        tableIndex: 5,
      });
    });
  });

  describe('getPageIndexByResourceType', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup({
        dashboards: { ...globalState.search.dashboards, page_index: 1 },
        tables: { ...globalState.search.tables, page_index: 2 },
        users: { ...globalState.search.users, page_index: 3 },
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('given ResourceType.dashboard, returns page_index from props for dashboards', () => {
      expect(wrapper.instance().getPageIndexByResourceType(ResourceType.dashboard)).toEqual(props.dashboards.page_index);
    });

    it('given ResourceType.table, returns page_index from props for tables', () => {
      expect(wrapper.instance().getPageIndexByResourceType(ResourceType.table)).toEqual(props.tables.page_index);
    });

    it('given ResourceType.user, returns page_index from props for users', () => {
      expect(wrapper.instance().getPageIndexByResourceType(ResourceType.user)).toEqual(props.users.page_index);
    });

    it('returns 0 if not given a supported ResourceType', () => {
      // @ts-ignore: cover default case
      expect(wrapper.instance().getPageIndexByResourceType('not valid')).toEqual(0);
    });
  });

  describe('onPaginationChange', () => {
    const testIndex = 10;
    let props;
    let wrapper;

    let searchResourceSpy;
    let updatePageUrlSpy;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      searchResourceSpy = jest.spyOn(props, 'searchResource');
      updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');

      wrapper.instance().onPaginationChange(testIndex);
    });

    it('calls props.searchResource with correct parameters', () => {
      expect(searchResourceSpy).toHaveBeenCalledWith(wrapper.state().selectedTab, props.searchTerm, testIndex);
    });

    it('calls updatePageUrl with correct parameters', () => {
      expect(updatePageUrlSpy).toHaveBeenCalledWith(props.searchTerm, wrapper.state().selectedTab, testIndex);
    });
  });

  describe('onTabChange', () => {
    const givenTab = ResourceType.user;
    const mockPageIndex = 2;
    let props;
    let wrapper;

    let getPageIndexByResourceTypeSpy;
    let getSelectedTabByResourceTypeSpy;
    let updatePageUrlSpy;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      getSelectedTabByResourceTypeSpy = jest.spyOn(wrapper.instance(), 'getSelectedTabByResourceType').mockImplementation(() => {
        return givenTab;
      });
      getPageIndexByResourceTypeSpy = jest.spyOn(wrapper.instance(), 'getPageIndexByResourceType').mockImplementation(() => {
        return mockPageIndex;
      });
      updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
      setStateSpy.mockClear();

      wrapper.instance().onTabChange(givenTab);
    });

    it('calls getSelectedTabByResourceType with correct parameters', () => {
      expect(getSelectedTabByResourceTypeSpy).toHaveBeenCalledWith(givenTab);
    });

    it('calls setState with correct parameters', () => {
      expect(setStateSpy).toHaveBeenCalledWith({ selectedTab: givenTab });
    });

    it('calls updatePageUrl with correct parameters', () => {
      expect(updatePageUrlSpy).toHaveBeenCalledWith(props.searchTerm, givenTab, mockPageIndex);
    });

    afterAll(() => {
      getSelectedTabByResourceTypeSpy.mockRestore();
      getPageIndexByResourceTypeSpy.mockRestore();
    });
  });

  describe('updatePageUrl', () => {
    it('pushes correct update to the window state', () => {
      const { props, wrapper } = setup();
      const pageIndex = 2;
      const searchTerm = 'testing';
      const tab = ResourceType.user;
      const expectedPath = `/search?searchTerm=${searchTerm}&selectedTab=${tab}&pageIndex=${pageIndex}`;
      const historyPushSpy = jest.spyOn(props.history, 'push');
      wrapper.instance().updatePageUrl(searchTerm, tab, pageIndex);
      expect(historyPushSpy).toHaveBeenCalledWith(expectedPath);
    });
  });

  describe('getTabContent', () => {
    let content;

    describe('if searchTerm but no results', () => {
      it('renders expected search error message', () => {
        const { props, wrapper } = setup({ searchTerm: 'data' });
        const testResults = {
          page_index: 0,
          results: [],
          total_results: 0,
        };
        content = shallow(wrapper.instance().getTabContent(testResults, TABLE_RESOURCE_TITLE));
        expect(content.children().at(0).text()).toEqual(`${SEARCH_ERROR_MESSAGE_PREFIX}data${SEARCH_ERROR_MESSAGE_INFIX}tables${SEARCH_ERROR_MESSAGE_SUFFIX}`);
      });
    });

    describe('if page index is out of bounds', () => {
      it('renders expected page index error message', () => {
        const { props, wrapper } = setup();
        const testResults = {
          page_index: 2,
          results: [],
          total_results: 1,
        };
        content = shallow(wrapper.instance().getTabContent(testResults, TABLE_RESOURCE_TITLE));
        expect(content.children().at(0).text()).toEqual(PAGE_INDEX_ERROR_MESSAGE);
      });
    });

    describe('if searchTerm and search results exist', () => {
      let props;
      let wrapper;
      beforeAll(() => {
        const setupResult = setup({ searchTerm: '' });
        props = setupResult.props;
        wrapper = setupResult.wrapper;
        content = shallow(wrapper.instance().getTabContent(props.tables, TABLE_RESOURCE_TITLE));
      });

      it('renders correct label for content', () => {
        expect(content.children().at(0).find('label').text()).toEqual(`1-1 of 1 results`);
      });

      it('renders InfoButton with correct props', () => {
        expect(content.children().at(0).find(InfoButton).props()).toMatchObject({
          infoText: SEARCH_INFO_TEXT,
        });
      });

      it('renders ResourceList with correct props', () => {
        const { props, wrapper } = setup();
        const testResults = {
          page_index: 0,
          results: [],
          total_results: 11,
        };
        content = shallow(wrapper.instance().getTabContent(testResults, TABLE_RESOURCE_TITLE));

        expect(content.children().find(ResourceList).props()).toMatchObject({
          activePage: 0,
          slicedItems: testResults.results,
          slicedItemsCount: testResults.total_results,
          itemsPerPage: RESULTS_PER_PAGE,
          onPagination: wrapper.instance().onPaginationChange,
          source: SEARCH_SOURCE_NAME,
        });
      });
    });
  });

  describe('renderContent', () => {
    it('renders search results when given search term', () => {
      const {props, wrapper} = setup({ searchTerm: 'test' });
      expect(wrapper.instance().renderContent()).toEqual(wrapper.instance().renderSearchResults());
    });

    it('renders loading spinner when in loading state', () => {
      const {props, wrapper} = setup({ isLoading: true });
      expect(wrapper.instance().renderContent()).toEqual(<LoadingSpinner/>);
    });
  });

  describe('renderSearchResults', () => {
    let props;
    let wrapper;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders TabsComponent with correct props', () => {
      AppConfig.indexUsers.enabled = false;
      const content = shallow(wrapper.instance().renderSearchResults());
      const tabProps = content.find(TabsComponent).props();
      expect(tabProps.activeKey).toEqual(wrapper.state().selectedTab);
      expect(tabProps.defaultTab).toEqual(ResourceType.table);
      expect(tabProps.onSelect).toEqual(wrapper.instance().onTabChange);

      const firstTab = tabProps.tabs[0];
      expect(firstTab.key).toEqual(ResourceType.table);
      expect(firstTab.title).toEqual(`${TABLE_RESOURCE_TITLE} (${props.tables.total_results})`);
      expect(firstTab.content).toEqual(wrapper.instance().getTabContent(props.tables, TABLE_RESOURCE_TITLE));
    });

    it('renders only one tab if people is disabled', () => {
      AppConfig.indexUsers.enabled = false;
      const content = shallow(wrapper.instance().renderSearchResults());
      const tabConfig = content.find(TabsComponent).props().tabs;
      expect(tabConfig.length).toEqual(1)
    });

    it('renders two tabs if indexUsers is enabled', () => {
      AppConfig.indexUsers.enabled = true;
      const content = shallow(wrapper.instance().renderSearchResults());
      const tabConfig = content.find(TabsComponent).props().tabs;
      expect(tabConfig.length).toEqual(2)
    });
  });

  describe('render', () => {
    describe('DocumentTitle', () => {
      it('renders correct title if there is a search term', () => {
        const { props, wrapper } = setup({ searchTerm: 'test search' });
        expect(wrapper.find(DocumentTitle).props()).toMatchObject({
          title: `test search${DOCUMENT_TITLE_SUFFIX}`
        });
      });

      it('does not render DocumentTitle if searchTerm is empty string', () => {
        const { props, wrapper } = setup({ searchTerm: '' });
        expect(wrapper.find(DocumentTitle).exists()).toBeFalsy();
      });
    });

    it('renders SearchBar with correct props', () => {
      const { props, wrapper } = setup();
      expect(wrapper.find(SearchBar).exists()).toBeTruthy();
    });

    it('calls renderSearchResults if searchTerm is not empty string', () => {
      const { props, wrapper } = setup({ searchTerm: 'test search' });
      const renderSearchResultsSpy = jest.spyOn(wrapper.instance(), 'renderSearchResults');
      wrapper.setProps(props);
      expect(renderSearchResultsSpy).toHaveBeenCalled();
    });
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets searchAll on the props', () => {
    expect(result.searchAll).toBeInstanceOf(Function);
  });

  it('sets searchResource on the props', () => {
    expect(result.searchResource).toBeInstanceOf(Function);
  });
});

describe('mapStateToProps', () => {
  let result;
  beforeAll(() => {
    result = mapStateToProps(globalState);
  });

  it('sets searchTerm on the props', () => {
    expect(result.searchTerm).toEqual(globalState.search.search_term);
  });

  it('sets isLoading on the props', () => {
    expect(result.isLoading).toEqual(globalState.search.isLoading);
  });

  it('sets tables on the props', () => {
    expect(result.tables).toEqual(globalState.search.tables);
  });

  it('sets users on the props', () => {
    expect(result.users).toEqual(globalState.search.users);
  });

  it('sets dashboards on the props', () => {
    expect(result.dashboards).toEqual(globalState.search.dashboards);
  });
});
