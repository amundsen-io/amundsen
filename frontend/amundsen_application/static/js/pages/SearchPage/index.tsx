// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import * as DocumentTitle from 'react-document-title';
import { RouteComponentProps } from 'react-router';
import { Search as UrlSearch } from 'history';

import PaginatedApiResourceList from 'components/ResourceList/PaginatedApiResourceList';
import ResourceListHeader from 'components/ResourceList/ResourceListHeader';
import ShimmeringResourceLoader from 'components/ShimmeringResourceLoader';

import { GlobalState } from 'ducks/rootReducer';
import { submitSearchResource, urlDidUpdate } from 'ducks/search/reducer';
import {
  DashboardSearchResults,
  FeatureSearchResults,
  SearchResults,
  SubmitSearchResourceRequest,
  TableSearchResults,
  UrlDidUpdateRequest,
  UserSearchResults,
} from 'ducks/search/types';

import { Resource, ResourceType, SearchType } from 'interfaces';
import { getSearchResultsPerPage } from 'config/config-utils';
import SearchPanel from './SearchPanel';
import SearchFilter from './SearchFilter';
import ResourceSelector from './ResourceSelector';

import {
  DOCUMENT_TITLE_SUFFIX,
  PAGE_INDEX_ERROR_MESSAGE,
  SEARCH_DEFAULT_MESSAGE,
  SEARCH_ERROR_MESSAGE_PREFIX,
  SEARCH_ERROR_MESSAGE_SUFFIX,
  SEARCH_SOURCE_NAME,
  DASHBOARD_RESOURCE_TITLE,
  FEATURE_RESOURCE_TITLE,
  TABLE_RESOURCE_TITLE,
  USER_RESOURCE_TITLE,
  SEARCHPAGE_TITLE,
} from './constants';

import './styles.scss';

export interface StateFromProps {
  hasFilters: boolean;
  searchTerm: string;
  resource: ResourceType;
  isLoading: boolean;
  tables: TableSearchResults;
  dashboards: DashboardSearchResults;
  features: FeatureSearchResults;
  users: UserSearchResults;
  didSearch: boolean;
}

export interface DispatchFromProps {
  setPageIndex: (pageIndex: number) => SubmitSearchResourceRequest;
  urlDidUpdate: (urlSearch: UrlSearch) => UrlDidUpdateRequest;
}

export type SearchPageProps = StateFromProps &
  DispatchFromProps &
  RouteComponentProps<any>;

export class SearchPage extends React.Component<SearchPageProps> {
  public static defaultProps: Partial<SearchPageProps> = {};

  componentDidMount() {
    const { location, urlDidUpdate: updateUrl } = this.props;
    updateUrl(location.search);
  }

  componentDidUpdate(prevProps: SearchPageProps) {
    const { location, urlDidUpdate: updateUrl } = this.props;
    if (location.search !== prevProps.location.search) {
      updateUrl(location.search);
    }
  }

  renderSearchResults = () => {
    const { resource, tables, users, dashboards, features } = this.props;
    switch (resource) {
      case ResourceType.table:
        return this.getTabContent(tables, ResourceType.table);
      case ResourceType.user:
        return this.getTabContent(users, ResourceType.user);
      case ResourceType.dashboard:
        return this.getTabContent(dashboards, ResourceType.dashboard);
      case ResourceType.feature:
        return this.getTabContent(features, ResourceType.feature);
      default:
        return null;
    }
  };

  generateTabLabel = (tab: ResourceType): string => {
    switch (tab) {
      case ResourceType.dashboard:
        return DASHBOARD_RESOURCE_TITLE;
      case ResourceType.feature:
        return FEATURE_RESOURCE_TITLE;
      case ResourceType.table:
        return TABLE_RESOURCE_TITLE;
      case ResourceType.user:
        return USER_RESOURCE_TITLE;
      default:
        return '';
    }
  };

  getTabContent = (results: SearchResults<Resource>, tab: ResourceType) => {
    const { hasFilters, searchTerm, setPageIndex, didSearch } = this.props;
    const { page_index, total_results } = results;
    const startIndex = getSearchResultsPerPage() * page_index + 1;
    const tabLabel = this.generateTabLabel(tab);

    const hasNoSearchInputOrAction =
      searchTerm.length === 0 &&
      (!hasFilters || !didSearch) &&
      total_results === 0;
    if (hasNoSearchInputOrAction) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {SEARCH_DEFAULT_MESSAGE}
          </div>
        </div>
      );
    }

    const hasNoResults =
      total_results === 0 && (searchTerm.length > 0 || hasFilters);
    if (hasNoResults) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {SEARCH_ERROR_MESSAGE_PREFIX}
            <i>{tabLabel.toLowerCase()}</i>
            {SEARCH_ERROR_MESSAGE_SUFFIX}
          </div>
        </div>
      );
    }

    const hasIndexOutOfBounds = page_index < 0 || startIndex > total_results;
    if (hasIndexOutOfBounds) {
      return (
        <div className="search-list-container">
          <div className="search-error body-placeholder">
            {PAGE_INDEX_ERROR_MESSAGE}
          </div>
        </div>
      );
    }

    const uniqueResourceTypes = [
      ...new Set(results.results.map(({ type }) => type)),
    ];

    return (
      <div className="search-list-container">
        <ResourceListHeader resourceTypes={uniqueResourceTypes} />
        <PaginatedApiResourceList
          activePage={page_index}
          onPagination={setPageIndex}
          itemsPerPage={getSearchResultsPerPage()}
          slicedItems={results.results}
          source={SEARCH_SOURCE_NAME}
          totalItemsCount={total_results}
        />
      </div>
    );
  };

  renderContent = () => {
    const { isLoading } = this.props;
    if (isLoading) {
      return <ShimmeringResourceLoader numItems={getSearchResultsPerPage()} />;
    }

    return this.renderSearchResults();
  };

  render() {
    const { searchTerm } = this.props;
    const innerContent = (
      <div className="search-page">
        <SearchPanel>
          <ResourceSelector />
          <SearchFilter />
        </SearchPanel>
        <main className="search-results">
          <h1 className="sr-only">{SEARCHPAGE_TITLE}</h1>
          {this.renderContent()}
        </main>
      </div>
    );
    if (searchTerm.length > 0) {
      return (
        <DocumentTitle title={`${searchTerm}${DOCUMENT_TITLE_SUFFIX}`}>
          {innerContent}
        </DocumentTitle>
      );
    }
    return innerContent;
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const resourceFilters = state.search.filters[state.search.resource];
  return {
    hasFilters: resourceFilters && Object.keys(resourceFilters).length > 0,
    searchTerm: state.search.search_term,
    resource: state.search.resource,
    isLoading: state.search.isLoading,
    tables: state.search.tables,
    users: state.search.users,
    dashboards: state.search.dashboards,
    features: state.search.features,
    didSearch: state.search.didSearch,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      urlDidUpdate,
      setPageIndex: (pageIndex: number) =>
        submitSearchResource({
          pageIndex,
          searchType: SearchType.PAGINATION,
          updateUrl: true,
        }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(SearchPage);
