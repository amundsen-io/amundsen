import * as React from 'react';
import { QueryResource } from 'interfaces';
import QueryListItem from '../QueryListItem';

import './styles.scss';

export interface QueryListProps {
  queries: QueryResource[];
}

class QueryList extends React.Component<QueryListProps> {
  render() {
    const { queries } = this.props;

    if (queries.length === 0) {
      return null;
    }

    const queryList = queries.map(({ name, query_text, url }) => (
      <QueryListItem
        key={`key:${name}`}
        text={query_text}
        url={url}
        name={name}
      />
    ));

    return (
      <ul className="query-list list-group" role="tablist">
        {queryList}
      </ul>
    );
  }
}

export default QueryList;
