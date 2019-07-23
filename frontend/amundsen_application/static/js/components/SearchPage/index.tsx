import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as DocumentTitle from 'react-document-title';
import * as qs from 'simple-query-string';
import { RouteComponentProps } from 'react-router';
import { Search } from 'history';

import AppConfig from 'config/config';
import LoadingSpinner from 'components/common/LoadingSpinner';
import InfoButton from 'components/common/InfoButton';
import ResourceList from 'components/common/ResourceList';
import TabsComponent from 'components/common/Tabs';
import SearchBar from './SearchBar';

import { GlobalState } from 'ducks/rootReducer';
import { searchAll, searchResource, updateSearchTab } from 'ducks/search/reducer';
import {
  DashboardSearchResults,
  SearchAllRequest,
  SearchResourceRequest,
  SearchResults,
  TableSearchResults,
  UpdateSearchTabRequest,
  UserSearchResults,
} from 'ducks/search/types';

import { Resource, ResourceType } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

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
} from './constants';

export interface StateFromProps {
  searchTerm: string;
  selectedTab: ResourceType;
  isLoading: boolean;
  tables: TableSearchResults;
  dashboards: DashboardSearchResults;
  users: UserSearchResults;
}

export interface DispatchFromProps {
  searchAll: (term: string, selectedTab: ResourceType, pageIndex: number) => SearchAllRequest;
  searchResource: (term: string, resource: ResourceType, pageIndex: number) => SearchResourceRequest;
  updateSearchTab: (selectedTab: ResourceType) => UpdateSearchTabRequest;
}

export type SearchPageProps = StateFromProps & DispatchFromProps & RouteComponentProps<any>;

export class SearchPage extends React.Component<SearchPageProps> {
  public static defaultProps: Partial<SearchPageProps> = {};

  constructor(props) {
    super(props);
  }

  componentDidMount() {
    const urlSearchParams = this.getUrlParams(this.props.location.search);
    const globalStateParams = this.getGlobalStateParams();

    if (this.shouldUpdateFromGlobalState(urlSearchParams, globalStateParams)) {
       this.updatePageUrl(globalStateParams.term, globalStateParams.tab, globalStateParams.index, true);

    } else if (this.shouldUpdateFromUrlParams(urlSearchParams, globalStateParams)) {
      this.props.searchAll(urlSearchParams.term, urlSearchParams.tab, urlSearchParams.index);
      this.updatePageUrl(urlSearchParams.term, urlSearchParams.tab, urlSearchParams.index, true);
    }
  }

  shouldUpdateFromGlobalState(urlParams, globalStateParams): boolean {
    return urlParams.term === '' && globalStateParams.term !== '';
  }

  shouldUpdateFromUrlParams(urlParams, globalStateParams): boolean {
    return urlParams.term !== '' && urlParams.term !== globalStateParams.term;
  }

  componentDidUpdate(prevProps: SearchPageProps) {
    const nextUrlParams = this.getUrlParams(this.props.location.search);
    const prevUrlParams = this.getUrlParams(prevProps.location.search);

    // If urlParams and globalState are synced, no need to update
    if (this.isUrlStateSynced(nextUrlParams)) return;

    // Capture any updates in URL
    if (this.shouldUpdateSearchTerm(nextUrlParams, prevUrlParams)) {
      this.props.searchAll(nextUrlParams.term, nextUrlParams.tab, nextUrlParams.index);

    } else if (this.shouldUpdateTab(nextUrlParams, prevUrlParams)) {
      this.props.updateSearchTab(nextUrlParams.tab)

    } else if (this.shouldUpdatePageIndex(nextUrlParams, prevUrlParams)) {
      this.props.searchResource(nextUrlParams.term, nextUrlParams.tab, nextUrlParams.index);
    }
  }

  isUrlStateSynced(urlParams): boolean {
    const globalStateParams = this.getGlobalStateParams();

    return urlParams.term === globalStateParams.term &&
      urlParams.tab === globalStateParams.tab &&
      urlParams.index === globalStateParams.index;
  }

  shouldUpdateSearchTerm(nextUrlParams, prevUrlParams): boolean {
    return nextUrlParams.term !== prevUrlParams.term;
  }

  shouldUpdateTab(nextUrlParams, prevUrlParams): boolean {
    return nextUrlParams.tab !== prevUrlParams.tab;
  }

  shouldUpdatePageIndex(nextUrlParams, prevUrlParams): boolean {
    return nextUrlParams.index !== prevUrlParams.index;
  }

  getSelectedTabByResourceType = (newTab: ResourceType): ResourceType => {
    switch(newTab) {
      case ResourceType.table:
      case ResourceType.user:
        return newTab;
      case ResourceType.dashboard:
      default:
        return this.props.selectedTab;
    }
  };

  getUrlParams(search: Search) {
    const urlParams = qs.parse(search);
    const { searchTerm, pageIndex, selectedTab } = urlParams;
    const index = parseInt(pageIndex, 10);
    return {
      term: (searchTerm || '').trim(),
      tab: this.getSelectedTabByResourceType(selectedTab),
      index: isNaN(index) ? 0 : index,
    };
  };

  getGlobalStateParams() {
    return {
      term: this.props.searchTerm,
      tab: this.props.selectedTab,
      index: this.getPageIndexByResourceType(this.props.selectedTab),
    };
  }


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

  onPaginationChange = (index: number): void => {
    this.updatePageUrl(this.props.searchTerm, this.props.selectedTab, index);
  };

  onTabChange = (tab: ResourceType): void => {
    const newTab = this.getSelectedTabByResourceType(tab);
    this.updatePageUrl(this.props.searchTerm, newTab, this.getPageIndexByResourceType(newTab));
  };

  updatePageUrl = (searchTerm: string, tab: ResourceType, pageIndex: number, replace: boolean = false): void => {
    const pathName = `/search?searchTerm=${searchTerm}&selectedTab=${tab}&pageIndex=${pageIndex}`;

    if (replace) {
      this.props.history.replace(pathName);
    } else {
      this.props.history.push(pathName);
    }
  };

  renderSearchResults = () => {
    const tabConfig = [
      {
        title: `${TABLE_RESOURCE_TITLE} (${ this.props.tables.total_results })`,
        key: ResourceType.table,
        content: this.getTabContent(this.props.tables, ResourceType.table),
      },
    ];
    if (AppConfig.indexUsers.enabled) {
      tabConfig.push({
        title: `Users (${ this.props.users.total_results })`,
        key: ResourceType.user,
        content: this.getTabContent(this.props.users, ResourceType.user),
      })
    }

    return (
      <div>
        <TabsComponent
          tabs={ tabConfig }
          defaultTab={ ResourceType.table }
          activeKey={ this.props.selectedTab }
          onSelect={ this.onTabChange }
        />
      </div>
    );
  };

  generateInfoText = (tab: ResourceType): string => {
    switch (tab) {
      case ResourceType.table:
        return `${SEARCH_INFO_TEXT_BASE}${SEARCH_INFO_TEXT_TABLE_SUFFIX}`;
      default:
        return SEARCH_INFO_TEXT_BASE;
    }
  };

  generateTabLabel = (tab: ResourceType): string => {
    switch (tab) {
      case ResourceType.table:
        return TABLE_RESOURCE_TITLE;
      case ResourceType.user:
        return USER_RESOURCE_TITLE;
      default:
        return '';
    }
  };

  getTabContent = (results: SearchResults<Resource>, tab: ResourceType) => {
    const { searchTerm } = this.props;
    const { page_index, total_results } = results;
    const startIndex = (RESULTS_PER_PAGE * page_index) + 1;
    const endIndex = RESULTS_PER_PAGE * (page_index + 1);
    const tabLabel = this.generateTabLabel(tab);

    // TODO - Move error messages into Tab Component
    // Check no results
    if (total_results === 0 && searchTerm.length > 0) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {SEARCH_ERROR_MESSAGE_PREFIX}<i>{ searchTerm }</i>{SEARCH_ERROR_MESSAGE_INFIX}{tabLabel.toLowerCase()}{SEARCH_ERROR_MESSAGE_SUFFIX}
          </div>
        </div>
      )
    }

    // Check page_index bounds
    if (page_index < 0 || startIndex > total_results) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {PAGE_INDEX_ERROR_MESSAGE}
          </div>
        </div>
      )
    }

    const title =`${startIndex}-${Math.min(endIndex, total_results)} of ${total_results} results`;
    const infoText = this.generateInfoText(tab);
    return (
      <div className="search-list-container">
        <div className="search-list-header">
          <label>{ title }</label>
          <InfoButton infoText={infoText}/>
        </div>
        <ResourceList
          slicedItems={ results.results }
          slicedItemsCount={ total_results }
          source={ SEARCH_SOURCE_NAME }
          itemsPerPage={ RESULTS_PER_PAGE }
          activePage={ page_index }
          onPagination={ this.onPaginationChange }
        />
      </div>
      );
  };

  renderContent = () => {
    if (this.props.isLoading) {
      return (<LoadingSpinner/>);
    }
    return this.renderSearchResults();
  };

  render() {
    const { searchTerm } = this.props;
    const innerContent = (
      <div className="container search-page">
        <div className="row">
          <div className="col-xs-12 col-md-offset-1 col-md-10">
            <SearchBar />
            { this.renderContent() }
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
    selectedTab: state.search.selectedTab,
    isLoading: state.search.isLoading,
    tables: state.search.tables,
    users: state.search.users,
    dashboards: state.search.dashboards,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ searchAll, searchResource, updateSearchTab }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(SearchPage);
