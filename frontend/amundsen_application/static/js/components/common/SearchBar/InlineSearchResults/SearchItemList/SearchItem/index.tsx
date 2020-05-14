import * as React from 'react';
import { connect } from 'react-redux'

import { logClick } from 'ducks/utilMethods';
import { ResourceType } from 'interfaces';

import Flag from 'components/common/Flag';
import LoadingSpinner from 'components/common/LoadingSpinner';

import { GlobalState } from 'ducks/rootReducer'

import { SEARCH_ITEM_NO_RESULTS } from 'components/common/SearchBar/InlineSearchResults/constants';

export interface StateFromProps {
  isLoading: boolean;
  hasResults: boolean;
}

export interface OwnProps {
  listItemText: string;
  onItemSelect: (resourceType: ResourceType, updateUrl: boolean) => void;
  searchTerm: string;
  resourceType: ResourceType;
}

export type SearchItemProps = StateFromProps & OwnProps;

export class SearchItem extends React.Component<SearchItemProps, {}> {
  onViewAllResults = (e) => {
    logClick(e);
    this.props.onItemSelect(this.props.resourceType, true);
  }

  renderIndicator = () => {
    if (this.props.isLoading) {
      return (<LoadingSpinner/>)
    }
    if (!this.props.hasResults) {
      return (
        <div className="search-item-indicator body-placeholder">
          { SEARCH_ITEM_NO_RESULTS }
        </div>
      )
    }
    return null;
  }

  render = () => {
    const { searchTerm, listItemText, resourceType } = this.props;
    return (
      <li className="list-group-item">
        <a
          id={`inline-searchitem-viewall:${resourceType}`}
          className="search-item-link"
          onClick={this.onViewAllResults}
          target='_blank'
        >
          <img className="icon icon-search" />
          <div className="title-2 search-item-info">
            <div className="search-term">{`${searchTerm}\u00a0`}</div>
            <div className="search-item-text">{listItemText}</div>
            { resourceType === ResourceType.dashboard && <Flag text="beta" labelStyle="default"/> }
          </div>
          { this.renderIndicator() }
        </a>
      </li>
    );
  }
};

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const { isLoading, dashboards, tables, users } = state.search.inlineResults;
  let hasResults = false;
  switch (ownProps.resourceType) {
    case ResourceType.dashboard:
      hasResults = dashboards.results.length > 0;
      break;
    case ResourceType.table:
      hasResults = tables.results.length > 0;
      break;
    case ResourceType.user:
      hasResults = users.results.length > 0;
    default:
      break;
  }
  return {
    isLoading,
    hasResults
  };
};

export default connect<StateFromProps, {}, OwnProps>(mapStateToProps)(SearchItem);
