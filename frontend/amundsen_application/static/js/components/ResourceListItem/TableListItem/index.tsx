// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { ResourceType, TableResource } from 'interfaces';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import BadgeList from 'features/BadgeList';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';
import { LoggingParams } from '../types';

export interface TableListItemProps {
  table: TableResource;
  logging: LoggingParams;
}

class TableListItem extends React.Component<TableListItemProps, {}> {
  getLink = () => {
    const { table, logging } = this.props;

    return (
      `/table_detail/${table.cluster}/${table.database}/${table.schema}/${table.name}` +
      `?index=${logging.index}&source=${logging.source}`
    );
  };

  generateResourceIconClass = (
    databaseId: string,
    resource: ResourceType
  ): string => `icon resource-icon ${getSourceIconClass(databaseId, resource)}`;

  render() {
    const { table } = this.props;

    return (
      <li className="list-group-item clickable">
        <Link
          className="resource-list-item table-list-item"
          to={this.getLink()}
        >
          <div className="resource-info">
            <span
              className={this.generateResourceIconClass(
                table.database,
                table.type
              )}
            />
            <div className="resource-info-text my-auto">
              <div className="resource-name">
                <div className="truncated">
                  {table.schema_description && (
                    <SchemaInfo
                      schema={table.schema}
                      table={table.name}
                      desc={table.schema_description}
                    />
                  )}
                  {!table.schema_description && `${table.schema}.${table.name}`}
                </div>
                <BookmarkIcon
                  bookmarkKey={table.key}
                  resourceType={table.type}
                />
              </div>
              <div className="body-secondary-3 truncated">
                {table.description}
              </div>
            </div>
          </div>
          <div className="resource-type">
            {getSourceDisplayName(table.database, table.type)}
          </div>
          <div className="resource-badges">
            {!!table.badges && table.badges.length > 0 && (
              <div>
                <div className="body-secondary-3">
                  <BadgeList badges={table.badges} />
                </div>
              </div>
            )}
            <img className="icon icon-right" alt="" />
          </div>
        </Link>
      </li>
    );
  }
}

export default TableListItem;
