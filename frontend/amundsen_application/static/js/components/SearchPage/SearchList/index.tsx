import * as React from 'react';
import ResourceListItem from 'components/common/ResourceListItem';
import { Resource } from 'interfaces';

export interface SearchListProps {
  results?: Resource[];
  params?: SearchListParams;
}

export interface SearchListParams {
  source?: string;
  paginationStartIndex?: number;
}

const SearchList: React.SFC<SearchListProps> = ({ results, params }) => {
  const { source, paginationStartIndex } = params;
  return (
    <ul className="list-group">
      {
        results.map((resource, index) => {
          const logging = { source, index: paginationStartIndex + index };
          return <ResourceListItem item={ resource } logging={ logging } key={ index } />;
        })
      }
    </ul>
  );
};

SearchList.defaultProps = {
  results: [],
  params: {},
};

export default SearchList;
