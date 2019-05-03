import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import Pagination from 'react-js-pagination';

import { shallow } from 'enzyme';

import { ResourceType } from 'components/common/ResourceListItem/types';
import { SearchPage, SearchPageProps, mapDispatchToProps, mapStateToProps } from '../';
import {
  DOCUMENT_TITLE_SUFFIX,
  PAGINATION_PAGE_RANGE,
  PAGE_INDEX_ERROR_MESSAGE,
  POPULAR_TABLES_INFO_TEXT,
  POPULAR_TABLES_LABEL,
  POPULAR_TABLES_SOURCE_NAME,
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
import SearchList from '../SearchList';

import globalState from 'fixtures/globalState';

describe('SearchPage', () => {
  const setStateSpy = jest.spyOn(SearchPage.prototype, 'setState');

  const setup = (propOverrides?: Partial<SearchPageProps>, useMount?: boolean) => {
    const props: SearchPageProps = {
      searchTerm: globalState.search.search_term,
      popularTables: globalState.popularTables,
      dashboards: globalState.search.dashboards,
      tables: globalState.search.tables,
      users: globalState.search.users,
      searchAll: jest.fn(),
      searchResource: jest.fn(),
      getPopularTables: jest.fn(),
      ...propOverrides
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
    let mockResourceType;
    let mockSearchOptions;

    let createSearchOptionsSpy;
    let getSelectedTabByResourceTypeSpy;
    let searchAllSpy;
    let updatePageUrlSpy;

    beforeAll(() => {
      window.history.pushState({}, '', '/search?searchTerm=testName&selectedTab=table&pageIndex=1');

      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      mockResourceType = ResourceType.user;
      getSelectedTabByResourceTypeSpy = jest.spyOn(wrapper.instance(), 'getSelectedTabByResourceType').mockImplementation(() => {
        return mockResourceType;
      });
      mockSearchOptions = {'dashboardIndex': 0, 'tableIndex': 0, 'userIndex': 1};
      createSearchOptionsSpy = jest.spyOn(wrapper.instance(), 'createSearchOptions').mockImplementation(() => {
        return mockSearchOptions;
      });
      searchAllSpy = jest.spyOn(props, 'searchAll');
      updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');
      setStateSpy.mockClear();

      wrapper.instance().componentDidMount();
    });

    it('calls props.getPopularTables', () => {
      expect(props.getPopularTables).toHaveBeenCalled();
    });

    it('calls getSelectedTabByResourceType with correct value', () => {
      expect(getSelectedTabByResourceTypeSpy).toHaveBeenCalledWith('table');
    });

    it('calls setState with result of getSelectedTabByResourceType', () => {
      expect(setStateSpy).toHaveBeenCalledWith({ selectedTab:  mockResourceType });
    });

    describe('when searchTerm in params is valid', () => {
      it('calls searchAll', () => {
        expect(searchAllSpy).toHaveBeenCalledWith('testName', mockSearchOptions);
      });

      it('calls updatePageUrl', () => {
        expect(updatePageUrlSpy).toHaveBeenCalledWith('testName', mockResourceType, '1');
      });
    });

    describe('when pageIndex in params is undefined', () => {
      beforeAll(() => {
        updatePageUrlSpy.mockClear();
        window.history.pushState({}, '', '/search?searchTerm=testName');
        wrapper.instance().componentDidMount();
      });
      it('uses 0 as pageIndex', () => {
        expect(updatePageUrlSpy).toHaveBeenCalledWith('testName', mockResourceType, 0);
      });
    });

    describe('when searchTerm in params is undefined', () => {
      beforeAll(() => {
        searchAllSpy.mockClear();
        updatePageUrlSpy.mockClear();
        window.history.pushState({}, '', '/search?selectedTab=table&pageIndex=1');
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
        window.history.pushState({}, '', `/search?searchTerm=&selectedTab=table&pageIndex=1`);
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
      getSelectedTabByResourceTypeSpy.mockRestore();
      createSearchOptionsSpy.mockRestore();
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
        dashboards: {...globalState.search.dashboards, page_index: 1},
        tables: {...globalState.search.tables, page_index: 2},
        users: {...globalState.search.users, page_index: 3},
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

  describe('onSearchBarSubmit', () => {
    let props;
    let wrapper;

    let searchAllSpy;
    let updatePageUrlSpy;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      searchAllSpy = jest.spyOn(props, 'searchAll');
      updatePageUrlSpy = jest.spyOn(wrapper.instance(), 'updatePageUrl');

      wrapper.instance().onSearchBarSubmit('searchTerm');
    });

    it('calls props.searchAll with correct parameters', () => {
      expect(searchAllSpy).toHaveBeenCalledWith('searchTerm');
    });

    it('call updatePageUrl with correct parameters', () => {
      expect(updatePageUrlSpy).toHaveBeenCalledWith('searchTerm', wrapper.state().selectedTab, 0);
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
      expect(searchResourceSpy).toHaveBeenCalledWith(wrapper.state().selectedTab, props.searchTerm, testIndex - 1);
    });

    it('calls updatePageUrl with correct parameters', () => {
      expect(updatePageUrlSpy).toHaveBeenCalledWith(props.searchTerm, wrapper.state().selectedTab, testIndex - 1);
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
      const pushStateSpy = jest.spyOn(window.history, 'pushState');
      wrapper.instance().updatePageUrl(searchTerm, tab, pageIndex);
      expect(pushStateSpy).toHaveBeenCalledWith({}, '', `${window.location.origin}${expectedPath}`);
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
        const setupResult = setup({ searchTerm: ''});
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

      it('renders SearchList with correct props', () => {
        expect(content.children().find(SearchList).props()).toMatchObject({
          results: props.tables.results,
          params: {
            source: SEARCH_SOURCE_NAME,
            paginationStartIndex: 0,
          },
        });
      });

      it('does not render Pagination if total_results <= RESULTS_PER_PAGE', () => {
        expect(content.children().find(Pagination).exists()).toBeFalsy()
      });

      it('renders Pagination with correct props if total_results > RESULTS_PER_PAGE', () => {
        const { props, wrapper } = setup();
        const testResults = {
          page_index: 0,
          results: [],
          total_results: 11,
        };
        content = shallow(wrapper.instance().getTabContent(testResults, TABLE_RESOURCE_TITLE));
        expect(content.children().find(Pagination).props()).toMatchObject({
          activePage: 1,
          itemsCountPerPage: RESULTS_PER_PAGE,
          totalItemsCount: 11,
          pageRangeDisplayed: PAGINATION_PAGE_RANGE,
          onChange: wrapper.instance().onPaginationChange,
        });
      });
    });
  });

  describe('renderPopularTables', () => {
    let content;
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup({ searchTerm: ''});
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      content = shallow(wrapper.instance().renderPopularTables());
    });
    it('renders correct label for content', () => {
      expect(content.children().at(0).find('label').text()).toEqual(POPULAR_TABLES_LABEL);
    });

    it('renders InfoButton with correct props', () => {
      expect(content.children().at(0).find(InfoButton).props()).toMatchObject({
        infoText: POPULAR_TABLES_INFO_TEXT,
      });
    });

    it('renders SearchList with correct props', () => {
      expect(content.children().find(SearchList).props()).toMatchObject({
        results: props.popularTables,
        params: {
          source: POPULAR_TABLES_SOURCE_NAME,
          paginationStartIndex: 0,
        },
      });
    });
  });

  describe('renderSearchResults', () => {
    it('renders TabsComponent with correct props', () => {
      const { props, wrapper } = setup({ searchTerm: 'test search' });
      const content = shallow(wrapper.instance().renderSearchResults());
      const expectedTabConfig = [
        {
          title: `${TABLE_RESOURCE_TITLE} (${ props.tables.total_results })`,
          key: ResourceType.table,
          content: wrapper.instance().getTabContent(props.tables, TABLE_RESOURCE_TITLE),
        }
      ];
      expect(content.find(TabsComponent).props()).toMatchObject({
        activeKey: wrapper.state().selectedTab,
        defaultTab: ResourceType.table,
        onSelect: wrapper.instance().onTabChange,
        tabs: expectedTabConfig,
      });
    });
  });

  describe('render', () => {
    describe('DocumentTitle', () => {
      it('renders correct title if there is a search term', () => {
        const { props, wrapper } = setup({ searchTerm: 'test search'});
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
      expect(wrapper.find(SearchBar).props()).toMatchObject({
        handleValueSubmit: wrapper.instance().onSearchBarSubmit,
        searchTerm: props.searchTerm,
      });
    });

    it('calls renderSearchResults if searchTerm is not empty string', () => {
      const { props, wrapper } = setup({ searchTerm: 'test search' });
      const renderSearchResultsSpy = jest.spyOn(wrapper.instance(), 'renderSearchResults');
      wrapper.setProps(props);
      expect(renderSearchResultsSpy).toHaveBeenCalled();
    });

    it('calls renderPopularTables is searchTerm is empty string', () => {
      const { props, wrapper } = setup({ searchTerm: '' });
      const renderPopularTablesSpy = jest.spyOn(wrapper.instance(), 'renderPopularTables');
      wrapper.setProps(props);
      expect(renderPopularTablesSpy).toHaveBeenCalled();
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

  it('sets getPopularTables on the props', () => {
    expect(result.getPopularTables).toBeInstanceOf(Function);
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

  it('sets popularTables on the props', () => {
    expect(result.popularTables).toEqual(globalState.popularTables);
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
