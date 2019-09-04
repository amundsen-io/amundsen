import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as History from 'history';

import { shallow } from 'enzyme';

import AppConfig from 'config/config';
import { ResourceType } from 'interfaces';
import { mapDispatchToProps, mapStateToProps, SearchPage, SearchPageProps } from '../';
import {
  DOCUMENT_TITLE_SUFFIX,
  PAGE_INDEX_ERROR_MESSAGE,
  RESULTS_PER_PAGE,
  SEARCH_ERROR_MESSAGE_INFIX,
  SEARCH_ERROR_MESSAGE_PREFIX,
  SEARCH_ERROR_MESSAGE_SUFFIX,
  SEARCH_INFO_TEXT_BASE,
  SEARCH_INFO_TEXT_TABLE_SUFFIX,
  SEARCH_SOURCE_NAME,
  TABLE_RESOURCE_TITLE,
  USER_RESOURCE_TITLE,
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
      selectedTab: ResourceType.table,
      isLoading: false,
      dashboards: globalState.search.dashboards,
      tables: globalState.search.tables,
      users: globalState.search.users,
      setResource: jest.fn(),
      setPageIndex: jest.fn(),
      urlDidUpdate: jest.fn(),
      ...routerProps,
      ...propOverrides,
    };
    const wrapper = shallow<SearchPage>(<SearchPage {...props} />)
    return { props, wrapper };
  };

  describe('componentDidMount', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup(null, {
        search: '/search?searchTerm=testName&selectedTab=table&pageIndex=1',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('calls getUrlParams and getGlobalStateParams', () => {
      wrapper.instance().componentDidMount();
      expect(props.urlDidUpdate).toHaveBeenCalledWith(props.location.search);
    });
  });

  describe('componentDidUpdate', () => {
    let props;
    let wrapper;

    let mockPrevProps;
    beforeAll(() => {
      const setupResult = setup(null, {
        search: '/search?searchTerm=testName&selectedTab=table&pageIndex=1',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      mockPrevProps = {
        searchTerm: 'previous',
        location: {
          search: '/search?searchTerm=previous&selectedTab=table&pageIndex=0',
          pathname: 'mockstr',
          state: jest.fn(),
          hash: 'mockstr',
        }
      };
    });

    it('calls urlDidUpdate when location.search changes', () => {
      props.urlDidUpdate.mockClear();
      wrapper.instance().componentDidUpdate(mockPrevProps);
      expect(props.urlDidUpdate).toHaveBeenCalledWith(props.location.search);
    });

    it('does not call urldidUpdate when location.search is the same', () => {
      props.urlDidUpdate.mockClear();
      wrapper.instance().componentDidUpdate(props);
      expect(props.urlDidUpdate).not.toHaveBeenCalled();
    });
  });

  describe('generateInfoText', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper;
    });

    it('returns correct text for ResourceType.table', () => {
      const text = wrapper.instance().generateInfoText(ResourceType.table);
      const expectedText = `${SEARCH_INFO_TEXT_BASE}${SEARCH_INFO_TEXT_TABLE_SUFFIX}`;
      expect(text).toEqual(expectedText);
    });

    it('returns correct text for the default case', () => {
      const text = wrapper.instance().generateInfoText(ResourceType.user);
      expect(text).toEqual(SEARCH_INFO_TEXT_BASE);
    });
  });

  describe('generateTabLabel', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper;
    });

    it('returns correct text for ResourceType.table', () => {
      const text = wrapper.instance().generateTabLabel(ResourceType.table);
      expect(text).toEqual(TABLE_RESOURCE_TITLE);
    });

    it('returns correct text for ResourceType.user', () => {
      const text = wrapper.instance().generateTabLabel(ResourceType.user);
      expect(text).toEqual(USER_RESOURCE_TITLE);
    });

    it('returns empty string for the default case', () => {
      const text = wrapper.instance().generateTabLabel(ResourceType.dashboard);
      expect(text).toEqual('');
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
        content = shallow(wrapper.instance().getTabContent(testResults, ResourceType.table));
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
        content = shallow(wrapper.instance().getTabContent(testResults, ResourceType.table));
        expect(content.children().at(0).text()).toEqual(PAGE_INDEX_ERROR_MESSAGE);
      });
    });

    describe('if searchTerm and search results exist', () => {
      let props;
      let wrapper;
      let generateInfoTextMockResults;
      beforeAll(() => {
        const setupResult = setup({ searchTerm: '' });
        props = setupResult.props;
        wrapper = setupResult.wrapper;
        generateInfoTextMockResults = 'test info text';
        jest.spyOn(wrapper.instance(), 'generateInfoText').mockImplementation(() => generateInfoTextMockResults);
        content = shallow(wrapper.instance().getTabContent(props.tables, ResourceType.table));
      });

      it('renders correct label for content', () => {
        expect(content.children().at(0).find('label').text()).toEqual(`1-1 of 1 results`);
      });

      it('renders InfoButton with correct props', () => {
        expect(content.children().at(0).find(InfoButton).props()).toMatchObject({
          infoText: generateInfoTextMockResults,
        });
      });

      it('renders ResourceList with correct props', () => {
        const { props, wrapper } = setup();
        const testResults = {
          page_index: 0,
          results: [],
          total_results: 11,
        };
        content = shallow(wrapper.instance().getTabContent(testResults, ResourceType.table));

        expect(content.children().find(ResourceList).props()).toMatchObject({
          activePage: 0,
          slicedItems: testResults.results,
          slicedItemsCount: testResults.total_results,
          itemsPerPage: RESULTS_PER_PAGE,
          onPagination: props.setPageIndex,
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
      expect(tabProps.activeKey).toEqual(props.selectedTab);
      expect(tabProps.defaultTab).toEqual(ResourceType.table);
      expect(tabProps.onSelect).toEqual(props.setResource);

      const firstTab = tabProps.tabs[0];
      expect(firstTab.key).toEqual(ResourceType.table);
      expect(firstTab.title).toEqual(`${TABLE_RESOURCE_TITLE} (${props.tables.total_results})`);
      expect(firstTab.content).toEqual(wrapper.instance().getTabContent(props.tables, firstTab.key));
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

  it('sets setResource on the props', () => {
    expect(result.setResource).toBeInstanceOf(Function);
  });

  it('sets setPageIndex on the props', () => {
    expect(result.setPageIndex).toBeInstanceOf(Function);
  });

  it('sets urlDidUpdate on the props', () => {
    expect(result.urlDidUpdate).toBeInstanceOf(Function);
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

  it('sets selectedTab on the props', () => {
    expect(result.selectedTab).toEqual(globalState.search.selectedTab);
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
