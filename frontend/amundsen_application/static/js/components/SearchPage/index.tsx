import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as DocumentTitle from 'react-document-title';
import * as qs from 'simple-query-string';
import Pagination from 'react-js-pagination';
import { RouteComponentProps } from 'react-router';

import SearchBar from './SearchBar';
import SearchList from './SearchList';

import InfoButton from 'components/common/InfoButton';
import { ResourceType, TableResource } from 'components/common/ResourceListItem/types';
import TabsComponent from 'components/common/Tabs';

import { GlobalState } from 'ducks/rootReducer';
import { searchAll, searchResource } from 'ducks/search/reducer';
import {
  DashboardSearchResults,
  SearchAllOptions,
  SearchAllRequest,
  SearchResourceRequest,
  TableSearchResults,
  UserSearchResults
} from 'ducks/search/types';
import { getPopularTables } from 'ducks/popularTables/reducer';
import { GetPopularTablesRequest } from 'ducks/popularTables/types';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import {
  DOCUMENT_TITLE_SUFFIX,
  PAGE_INDEX_ERROR_MESSAGE,
  PAGINATION_PAGE_RANGE,
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
} from './constants';

export interface StateFromProps {
  searchTerm: string;
  popularTables: TableResource[];
  tables: TableSearchResults;
  dashboards: DashboardSearchResults;
  users: UserSearchResults;
}

export interface DispatchFromProps {
  searchAll: (term: string, options?: SearchAllOptions) => SearchAllRequest;
  searchResource: (resource: ResourceType, term: string, pageIndex: number) => SearchResourceRequest;
  getPopularTables: () => GetPopularTablesRequest;
}

export type SearchPageProps = StateFromProps & DispatchFromProps & RouteComponentProps<any>;

interface SearchPageState {
  selectedTab: ResourceType;
}

export class SearchPage extends React.Component<SearchPageProps, SearchPageState> {
  public static defaultProps: Partial<SearchPageProps> = {};

  constructor(props) {
    super(props);

    this.state = {
      selectedTab: ResourceType.table,
    };
  }

  componentDidMount() {
    this.props.getPopularTables();
    const params = qs.parse(this.props.location.search);
    const { searchTerm, pageIndex, selectedTab } = params;
    const { term, index, currentTab } = this.getSanitizedUrlParams(searchTerm, pageIndex, selectedTab);
    this.setState({ selectedTab: currentTab });
    if (term !== "") {
      this.props.searchAll(term, this.createSearchOptions(index, currentTab));
      if (currentTab !== selectedTab || pageIndex !== index) {
        this.updatePageUrl(term, currentTab, index);
      }
    }
  }

  componentDidUpdate(prevProps) {
    if (this.props.location.search !== prevProps.location.search) {
      const params = qs.parse(this.props.location.search);
      const { searchTerm, pageIndex, selectedTab } = params;
      const { term, index, currentTab } = this.getSanitizedUrlParams(searchTerm, pageIndex, selectedTab);
      this.setState({ selectedTab: currentTab });
      this.props.searchAll(term, this.createSearchOptions(index, currentTab));
    }
  }

  getSelectedTabByResourceType = (newTab: ResourceType): ResourceType => {
    switch(newTab) {
      case ResourceType.table:
      case ResourceType.user:
        return newTab;
      case ResourceType.dashboard:
      default:
        return this.state.selectedTab;
    }
  };

  createSearchOptions = (pageIndex: number, selectedTab: ResourceType) => {
    return {
      dashboardIndex: (selectedTab === ResourceType.dashboard) ? pageIndex : 0,
      userIndex: (selectedTab === ResourceType.user) ? pageIndex : 0,
      tableIndex: (selectedTab === ResourceType.table) ? pageIndex : 0,
    };
  };

  getSanitizedUrlParams = (searchTerm: string, pageIndex: number, selectedTab: ResourceType) => {
    const currentTab = this.getSelectedTabByResourceType(selectedTab);
    const index = pageIndex || 0;
    const term = searchTerm ? searchTerm : "";
    return {term, index, currentTab};
  };

  getPageIndexByResourceType = (tab: ResourceType): number => {
    switch(tab) {
      case ResourceType.table:
        return this.props.tables.page_index;
      case ResourceType.user:
        return this.props.users.page_index;
      case ResourceType.dashboard:
        return this.props.dashboards.page_index;
    }
    return 0;
  };

  onSearchBarSubmit = (searchTerm: string): void => {
    this.updatePageUrl(searchTerm, this.state.selectedTab,0);
  };

  onPaginationChange = (pageNumber: number): void => {
    const index = pageNumber - 1;
    this.props.searchResource(this.state.selectedTab, this.props.searchTerm, index);
    this.updatePageUrl(this.props.searchTerm, this.state.selectedTab, index);
  };

  onTabChange = (tab: ResourceType): void => {
    const currentTab = this.getSelectedTabByResourceType(tab);
    this.setState({ selectedTab: currentTab });
    this.updatePageUrl(this.props.searchTerm, currentTab, this.getPageIndexByResourceType(currentTab));
  };

  updatePageUrl = (searchTerm: string, tab: ResourceType, pageIndex: number): void => {
    const pathName = `/search?searchTerm=${searchTerm}&selectedTab=${tab}&pageIndex=${pageIndex}`;
    this.props.history.push(pathName);
  };

  renderPopularTables = () => {
    const searchListParams = {
      source: POPULAR_TABLES_SOURCE_NAME,
      paginationStartIndex: 0,
    };
    return (
        <div className="search-list-container">
          <div className="popular-tables-header">
            <label className="title-1">{POPULAR_TABLES_LABEL}</label>
            <InfoButton infoText={POPULAR_TABLES_INFO_TEXT}/>
          </div>
          <SearchList results={ this.props.popularTables } params={ searchListParams }/>
        </div>
      )
  };

  renderSearchResults = () => {
    const tabConfig = [
      {
        title: `${TABLE_RESOURCE_TITLE} (${ this.props.tables.total_results })`,
        key: ResourceType.table,
        content: this.getTabContent(this.props.tables, TABLE_RESOURCE_TITLE),
      },
      // TODO PEOPLE - Add users tab
    ];

    return (
      <div>
        <TabsComponent
          tabs={ tabConfig }
          defaultTab={ ResourceType.table }
          activeKey={ this.state.selectedTab }
          onSelect={ this.onTabChange }
        />
      </div>
    );
  };

  getTabContent = (results, tabLabel) => {
    const { searchTerm } = this.props;
    const { page_index, total_results } = results;
    const startIndex = (RESULTS_PER_PAGE * page_index) + 1;
    const endIndex = RESULTS_PER_PAGE * (page_index + 1);

    // TODO - Move error messages into Tab Component
    // Check no results
    if (total_results === 0 && searchTerm.length > 0) {
      return (
        <div className="search-list-container">
          <div className="search-error">
            {SEARCH_ERROR_MESSAGE_PREFIX}<i>{ searchTerm }</i>{SEARCH_ERROR_MESSAGE_INFIX}{tabLabel.toLowerCase()}{SEARCH_ERROR_MESSAGE_SUFFIX}
          </div>
        </div>
      )
    }

    // Check page_index bounds
    if (page_index < 0 || startIndex > total_results) {
      return (
        <div className="search-list-container">
          <div className="search-error">
            {PAGE_INDEX_ERROR_MESSAGE}
          </div>
        </div>
      )
    }

    const title =`${startIndex}-${Math.min(endIndex, total_results)} of ${total_results} results`;
    return (
      <div className="search-list-container">
        <div className="search-list-header">
          <label>{ title }</label>
          <InfoButton infoText={SEARCH_INFO_TEXT}/>
        </div>
        <SearchList results={ results.results } params={ {source: SEARCH_SOURCE_NAME, paginationStartIndex: 0 } }/>
        <div className="search-pagination-component">
            {
              total_results > RESULTS_PER_PAGE &&
              <Pagination
                activePage={ page_index + 1 }
                itemsCountPerPage={ RESULTS_PER_PAGE }
                totalItemsCount={ total_results }
                pageRangeDisplayed={ PAGINATION_PAGE_RANGE }
                onChange={ this.onPaginationChange }
              />
            }
        </div>
      </div>
      );
  };

  render() {
    const { searchTerm } = this.props;
    const innerContent = (
      <div className="container search-page">
        <div className="row">
          <div className="col-xs-12 col-md-offset-1 col-md-10">
            <SearchBar handleValueSubmit={ this.onSearchBarSubmit } searchTerm={ searchTerm }/>
            { searchTerm.length > 0 && this.renderSearchResults() }
            { searchTerm.length === 0 && this.renderPopularTables()  }
          </div>
        </div>
      </div>
    );
    if (searchTerm.length > 0) {
      return (
        <DocumentTitle title={ `${searchTerm}${DOCUMENT_TITLE_SUFFIX}` }>
          { innerContent }
        </DocumentTitle>
      );
    }
    return innerContent;
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    searchTerm: state.search.search_term,
    popularTables: state.popularTables,
    tables: state.search.tables,
    users: state.search.users,
    dashboards: state.search.dashboards,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ searchAll, searchResource, getPopularTables } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(SearchPage);
