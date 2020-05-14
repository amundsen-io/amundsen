import * as React from 'react';

import "./styles.scss";

export interface QueryListProps {
  queries: string[];
}

class QueryList extends React.Component<QueryListProps> {
  render() {
    const queries = this.props.queries;
    if (queries.length === 0) {
      return null;
    }

    return (
      <ul className="query-list list-group">
        {
          queries.map((query, index)=>
            (
              <li key={index} className="query-list-item list-group-item">
                <div className="title-2 truncated">
                  { query }
                </div>
              </li>
            )
          )
        }
      </ul>
    )
  }
}

export default QueryList;
