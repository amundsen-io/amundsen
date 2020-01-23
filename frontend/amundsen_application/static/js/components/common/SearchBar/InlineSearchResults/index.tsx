import * as React from 'react';
import { connect } from 'react-redux'

import SearchItemList from './SearchItemList';
import ResultItemList from './ResultItemList';

import { getDatabaseDisplayName, getDatabaseIconClass, indexUsersEnabled } from 'config/config-utils';

import { GlobalState } from 'ducks/rootReducer'
import { SearchResults, TableSearchResults, UserSearchResults } from 'ducks/search/types';

import { Resource, ResourceType, TableResource, UserResource } from 'interfaces';

import './styles.scss';

import * as CONSTANTS from './constants';

export interface StateFromProps {
  isLoading: boolean;
  tables: TableSearchResults;
  users: UserSearchResults;
}

export interface OwnProps {
  className?: string;
  onItemSelect: (resourceType: ResourceType, updateUrl?: boolean) => void;
  searchTerm: string;
}

export type InlineSearchResultsProps = StateFromProps & OwnProps;

export interface SuggestedResult {
  href: string;
  iconClass: string;
  subtitle: string;
  title: string;
  type: string;
}

export class InlineSearchResults extends React.Component<InlineSearchResultsProps, {}> {
  constructor(props) {
    super(props);
  }

  getTitleForResource = (resourceType: ResourceType): string => {
    switch (resourceType) {
      case ResourceType.table:
        return CONSTANTS.DATASETS;
      case ResourceType.user:
        return CONSTANTS.PEOPLE;
      default:
        return '';
    }
  };

  getTotalResultsForResource = (resourceType: ResourceType) : number => {
    switch (resourceType) {
      case ResourceType.table:
        return this.props.tables.total_results
      case ResourceType.user:
        return this.props.users.total_results;
      default:
        return 0;
    }
  };

  getResultsForResource = (resourceType: ResourceType): Resource[] => {
    switch (resourceType) {
      case ResourceType.table:
        return this.props.tables.results.slice(0, 2);
      case ResourceType.user:
        return this.props.users.results.slice(0, 2);
      default:
        return [];
    }
  };

  getSuggestedResultsForResource = (resourceType: ResourceType): SuggestedResult[] => {
    const results = this.getResultsForResource(resourceType);
    return results.map((result, index) => {
      return {
        href: this.getSuggestedResultHref(resourceType, result, index),
        iconClass: this.getSuggestedResultIconClass(resourceType, result),
        subtitle: this.getSuggestedResultSubTitle(resourceType, result),
        title: this.getSuggestedResultTitle(resourceType, result),
        type: this.getSuggestedResultType(resourceType, result)
      }
    });
  };

  getSuggestedResultHref = (resourceType: ResourceType, result: Resource, index: number): string => {
    const logParams = `source=inline_search&index=${index}`;
    switch (resourceType) {
      case ResourceType.table:
        const table = result as TableResource;
        return `/table_detail/${table.cluster}/${table.database}/${table.schema_name}/${table.name}?${logParams}`;
      case ResourceType.user:
        const user = result as UserResource;
        return `/user/${user.user_id}?${logParams}`;
      default:
        return '';
    }
  };

  getSuggestedResultIconClass = (resourceType: ResourceType, result: Resource): string => {
    switch (resourceType) {
      case ResourceType.table:
        const table = result as TableResource;
        return getDatabaseIconClass(table.database);
      case ResourceType.user:
        return CONSTANTS.USER_ICON_CLASS;
      default:
        return '';
    }
  };

  getSuggestedResultSubTitle = (resourceType: ResourceType, result: Resource): string => {
    switch (resourceType) {
      case ResourceType.table:
        const table = result as TableResource;
        return table.description;
      case ResourceType.user:
        const user = result as UserResource;
        return user.team_name;
      default:
        return '';
    }
  };

  getSuggestedResultTitle = (resourceType: ResourceType, result: Resource): string => {
    switch (resourceType) {
      case ResourceType.table:
        const table = result as TableResource;
        return `${table.schema_name}.${table.name}`;
      case ResourceType.user:
        const user = result as UserResource;
        return user.display_name;
      default:
        return '';
    }
  };

  getSuggestedResultType = (resourceType: ResourceType, result: Resource): string => {
    switch (resourceType) {
      case ResourceType.table:
        const table = result as TableResource;
        return getDatabaseDisplayName(table.database);
      case ResourceType.user:
        return CONSTANTS.PEOPLE_USER_TYPE;
      default:
        return '';
    }
  };

  renderResultsByResource = (resourceType: ResourceType) => {
    const suggestedResults = this.getSuggestedResultsForResource(resourceType);
    if (suggestedResults.length === 0) {
      return null;
    }
    return (
      <div className="inline-results-section">
        <ResultItemList
          onItemSelect={this.props.onItemSelect}
          resourceType={resourceType}
          searchTerm={this.props.searchTerm}
          suggestedResults={suggestedResults}
          totalResults={this.getTotalResultsForResource(resourceType)}
          title={this.getTitleForResource(resourceType)}
        />
      </div>
    )
  };

  renderResults = () => {
    if (this.props.isLoading) {
      return null;
    }
    return (
      <>
        { this.renderResultsByResource(ResourceType.table) }
        {
          indexUsersEnabled() &&
          this.renderResultsByResource(ResourceType.user)
        }
      </>
    );
  }

  render() {
    const { className = '', onItemSelect, searchTerm } = this.props;
    return (
      <div id="inline-results" className={`inline-results ${className}`}>
        <div className="inline-results-section search-item-section">
          <SearchItemList
            onItemSelect={onItemSelect}
            searchTerm={searchTerm}
          />
        </div>
        { this.renderResults() }
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const { isLoading, tables, users } = state.search.inlineResults;
  return {
    isLoading,
    tables,
    users,
  };
};

export default connect<StateFromProps, OwnProps>(mapStateToProps)(InlineSearchResults);
