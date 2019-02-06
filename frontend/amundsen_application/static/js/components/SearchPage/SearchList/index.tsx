import * as React from 'react';
import SearchListItem from './SearchListItem';
import { SearchListResult } from '../types';

interface SearchListProps {
  results?: SearchListResult[];
  params?: SearchListParams;
}

interface SearchListParams {
  source?: string;
  paginationStartIndex?: number;
}

const SearchList: React.SFC<SearchListProps> = ({ results, params }) => {
  const { source , paginationStartIndex } = params;
  const resultMap = results.map((entry, i) =>
    <SearchListItem
      key={ entry.key }
      params={{source, index: paginationStartIndex + i}}
      title={`${entry.schema_name}.${entry.name}`}
      subtitle={ entry.description }
      lastUpdated = { entry.last_updated }
      schema={ entry.schema_name }
      cluster={ entry.cluster }
      table={ entry.name }
      db={ entry.database }
  />);
  return (
    <ul className="list-group">
      { resultMap }
    </ul>
  );
};

SearchList.defaultProps = {
  results: [],
  params: {},
};

export default SearchList;
