import * as React from 'react';
import { Link } from 'react-router-dom';

import { LoggingParams } from '../types';

import { TableResource } from 'interfaces';

import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';

import { getDatabaseDisplayName, getDatabaseIconClass } from 'config/config-utils';

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
    const dateTokens = new Date(table.last_updated_timestamp * 1000).toDateString().split(' ');
    return `${dateTokens[1]} ${dateTokens[2]}, ${dateTokens[3]}`;
  };

  getLink = () => {
    const { table, logging } = this.props;
    return `/table_detail/${table.cluster}/${table.database}/${table.schema}/${table.name}`
      + `?index=${logging.index}&source=${logging.source}`;
  };

  generateResourceIconClass = (databaseId: string): string => {
    return `icon resource-icon ${getDatabaseIconClass(databaseId)}`;
  };

  render() {
    const { table } = this.props;
    const hasLastUpdated = !!table.last_updated_timestamp;

    return (
      <li className="list-group-item">
        <Link className="resource-list-item table-list-item" to={ this.getLink() }>
          <div className="resource-info">
            <img className={this.generateResourceIconClass(table.database)} />
            <div className="resource-info-text">
              <div className="resource-name title-2">
                <div className="truncated">
                  { `${table.schema}.${table.name}`}
                </div>
                <BookmarkIcon bookmarkKey={ this.props.table.key }/>
              </div>
              <div className="body-secondary-3 truncated">{ table.description }</div>
            </div>
          </div>
          <div className="resource-type">
            { getDatabaseDisplayName(table.database) }
          </div>
          <div className="resource-badges">
            {
              hasLastUpdated &&
              <div>
                <div className="title-3">Last Updated</div>
                <div className="body-secondary-3">
                  { this.getDateLabel() }
                </div>
              </div>
            }
            <img className="icon icon-right" />
          </div>
        </Link>
      </li>
    );
  }
}

export default TableListItem;
