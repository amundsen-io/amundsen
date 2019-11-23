import * as React from 'react';

import { logClick } from 'ducks/utilMethods';
import { ResourceType } from 'interfaces';

export interface SearchItemProps {
  listItemText: string;
  onItemSelect: (resourceType: ResourceType, updateUrl: boolean) => void;
  searchTerm: string;
  resourceType: ResourceType;
}

class SearchItem extends React.Component<SearchItemProps, {}> {
  constructor(props) {
    super(props);
  }

  onViewAllResults = (e) => {
    logClick(e);
    this.props.onItemSelect(this.props.resourceType, true);
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
          </div>
        </a>
      </li>
    );
  }
};

export default SearchItem;
