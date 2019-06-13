import * as React from 'react';
import { Link } from 'react-router-dom';

import { LoggingParams } from '../types';

import { TableResource } from 'interfaces';

import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';

export interface TableListItemProps {
  table: TableResource;
  logging: LoggingParams;
}

class TableListItem extends React.Component<TableListItemProps, {}> {
  constructor(props) {
    super(props);
  }

  getDateLabel = () => {
    const { table } = this.props;
    const dateTokens = new Date(table.last_updated_epoch * 1000).toDateString().split(' ');
    return `${dateTokens[1]} ${dateTokens[2]}, ${dateTokens[3]}`;
  };

  getLink = () => {
    const { table, logging } = this.props;
    return `/table_detail/${table.cluster}/${table.database}/${table.schema_name}/${table.name}`
      + `?index=${logging.index}&source=${logging.source}`;
  };

  render() {
    const { table } = this.props;
    const hasLastUpdated = !!table.last_updated_epoch;

    return (
      <li className="list-group-item">
        <Link className="resource-list-item table-list-item" to={ this.getLink() }>
          <img className="icon icon-database icon-color" />
          <div className="content">
            <div className={ hasLastUpdated? "col-sm-9 col-md-10" : "col-sm-12"}>
              <div className="resource-name title-2">
                <div className="truncated">
                  { `${table.schema_name}.${table.name}`}
                </div>
                <BookmarkIcon bookmarkKey={ this.props.table.key }/>
              </div>
              <div className="body-secondary-3 truncated">{ table.description }</div>
            </div>
            {
              hasLastUpdated &&
              <div className="hidden-xs col-sm-3 col-md-2">
                <div className="title-3">Last Updated</div>
                <div className="body-secondary-3 truncated">
                  { this.getDateLabel() }
                </div>
              </div>
            }
          </div>
          <img className="icon icon-right" />
        </Link>
      </li>
    );
  }
}

export default TableListItem;
