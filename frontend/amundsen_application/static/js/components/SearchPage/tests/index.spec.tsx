import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as History from 'history';

import { shallow } from 'enzyme';

import { ResourceType } from 'interfaces';
import { mapDispatchToProps, mapStateToProps, SearchPage, SearchPageProps } from '../';
import {
  DOCUMENT_TITLE_SUFFIX,
  PAGE_INDEX_ERROR_MESSAGE,
  RESULTS_PER_PAGE,
  SEARCH_DEFAULT_MESSAGE,
  SEARCH_ERROR_MESSAGE_PREFIX,
  SEARCH_ERROR_MESSAGE_SUFFIX,
  SEARCH_SOURCE_NAME,
  TABLE_RESOURCE_TITLE,
  USER_RESOURCE_TITLE,
} from '../constants';

import LoadingSpinner from 'components/common/LoadingSpinner';
import ResourceSelector from 'components/SearchPage/ResourceSelector';
import SearchFilter from 'components/SearchPage/SearchFilter';
import SearchPanel from 'components/SearchPage/SearchPanel';
import ResourceList from 'components/common/ResourceList';

import globalState from 'fixtures/globalState';
import { defaultEmptyFilters, datasetFilterExample } from 'fixtures/search/filters';
import { getMockRouterProps } from 'fixtures/mockRouter';

describe('SearchPage', () => {
  const setStateSpy = jest.spyOn(SearchPage.prototype, 'setState');
  const setup = (propOverrides?: Partial<SearchPageProps>, location?: Partial<History.Location>) => {
    const routerProps = getMockRouterProps<any>(null, location);
    const props: SearchPageProps = {
      hasFilters: false,
      searchTerm: globalState.search.search_term,
      resource: ResourceType.table,
      isLoading: false,
      dashboards: globalState.search.dashboards,
      tables: globalState.search.tables,
      users: globalState.search.users,
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
        search: '/search?searchTerm=testName&resource=table&pageIndex=1',
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
        search: '/search?searchTerm=testName&resource=table&pageIndex=1',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      mockPrevProps = {
        searchTerm: 'previous',
        location: {
          search: '/search?searchTerm=previous&resource=table&pageIndex=0',
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
    describe('if no search input (no term or filters)', () => {
      it('renders default search page message', () => {
        const { props, wrapper } = setup({ searchTerm: '', hasFilters: false });
        content = shallow(wrapper.instance().getTabContent({
          page_index: 0,
          results: [],
          total_results: 0,
        }, ResourceType.table));
        expect(content.children().at(0).text()).toEqual(SEARCH_DEFAULT_MESSAGE);
      });
    });

    describe('if no search results, renders expected search error message', () => {
      let testResults;
      beforeAll(() => {
        testResults = {
          page_index: 0,
          results: [],
          total_results: 0,
        };
      })
      it('if there is a searchTerm ', () => {
        const { props, wrapper } = setup({ searchTerm: 'data' });
        content = shallow(wrapper.instance().getTabContent(testResults, ResourceType.table));
        const message = `${SEARCH_ERROR_MESSAGE_PREFIX}${TABLE_RESOURCE_TITLE.toLowerCase()}${SEARCH_ERROR_MESSAGE_SUFFIX}`;
        expect(content.children().at(0).text()).toEqual(message);
      });

      it('if no searchTerm but there are filters active', () => {
        const { props, wrapper } = setup({ searchTerm: '', hasFilters: true });
        content = shallow(wrapper.instance().getTabContent(testResults, ResourceType.table));
        const message = `${SEARCH_ERROR_MESSAGE_PREFIX}${TABLE_RESOURCE_TITLE.toLowerCase()}${SEARCH_ERROR_MESSAGE_SUFFIX}`;
        expect(content.children().at(0).text()).toEqual(message);
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
        content = shallow(wrapper.instance().getTabContent(props.tables, ResourceType.table));
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
    it('renders the correct content for table resources', () => {
      const { props, wrapper } = setup({
        resource: ResourceType.table
      });
      const getTabContentSpy = jest.spyOn(wrapper.instance(), 'getTabContent');
      shallow(wrapper.instance().renderSearchResults());
      expect(getTabContentSpy).toHaveBeenCalledWith(props.tables, ResourceType.table);
    });

    it('renders the correct content for user resources', () => {
      const { props, wrapper } = setup({
        resource: ResourceType.user
      });
      const getTabContentSpy = jest.spyOn(wrapper.instance(), 'getTabContent');
      shallow(wrapper.instance().renderSearchResults());
      expect(getTabContentSpy).toHaveBeenCalledWith(props.users, ResourceType.user);
    });

    it('renders the correct content for dashboard resources', () => {
      const { props, wrapper } = setup({
        resource: ResourceType.dashboard
      });
      const getTabContentSpy = jest.spyOn(wrapper.instance(), 'getTabContent');
      shallow(wrapper.instance().renderSearchResults());
      expect(getTabContentSpy).toHaveBeenCalledWith(props.dashboards, ResourceType.dashboard);
    });

    it('renders null for an invalid resource', () => {
      const { props, wrapper } = setup({
        resource: null
      });
      const renderedSearchResults = wrapper.instance().renderSearchResults();
      expect(renderedSearchResults).toBe(null);
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

    it('calls renderSearchResults if searchTerm is not empty string', () => {
      const { props, wrapper } = setup({ searchTerm: 'test search' });
      const renderSearchResultsSpy = jest.spyOn(wrapper.instance(), 'renderSearchResults');
      wrapper.setProps(props);
      expect(renderSearchResultsSpy).toHaveBeenCalled();
    });
  });

  describe('renders a SearchPanel', () => {
    let props;
    let wrapper;
    let searchPanel;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      searchPanel = wrapper.find(SearchPanel);
    })
    it('renders a search panel', () => {
      expect(searchPanel.exists()).toBe(true);
    });
    it('renders ResourceSelector as SearchPanel child', () => {
      expect(searchPanel.find(ResourceSelector).exists()).toBe(true);
    });
    it('renders SearchFilter as SearchPanel child', () => {
      expect(searchPanel.find(SearchFilter).exists()).toBe(true);
    });
  })

});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
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

  it('sets resource on the props', () => {
    expect(result.resource).toEqual(globalState.search.resource);
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

  describe('sets hasFilters on the props', () => {
    it('sets fo falsy value if selected resource has no filters', () => {
      const testState = {
        ...globalState
      };
      testState.search.resource = ResourceType.user;
      testState.search.filters = defaultEmptyFilters;
      result = mapStateToProps(testState);
      expect(result.hasFilters).toBeFalsy();
    })

    it('sets true if selected resource has filters', () => {
      const testState = {
        ...globalState
      };
      testState.search.resource = ResourceType.table;
      testState.search.filters = datasetFilterExample;
      result = mapStateToProps(testState);
      expect(result.hasFilters).toBe(true);
    })
  });
});
