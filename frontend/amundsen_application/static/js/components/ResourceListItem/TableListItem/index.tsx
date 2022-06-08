// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { ResourceType, TableResource } from 'interfaces';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import BadgeList from 'features/BadgeList';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';
import { logClick } from 'utils/analytics';
import { LoggingParams } from '../types';
import MetadataHighlightList from '../MetadataHighlightList';
import { HighlightedTable } from '../MetadataHighlightList/utils';

export interface TableListItemProps {
  table: TableResource;
  logging: LoggingParams;
  tableHighlights: HighlightedTable;
}

export const getLink = (table, logging) =>
  `/table_detail/${table.cluster}/${table.database}/${table.schema}/${table.name}` +
  `?index=${logging.index}&source=${logging.source}`;

export const generateResourceIconClass = (databaseId: string): string =>
  `icon resource-icon ${getSourceIconClass(databaseId, ResourceType.table)}`;

const TableListItem: React.FC<TableListItemProps> = ({
  table,
  logging,
  tableHighlights,
}) => (
  <li className="list-group-item clickable">
    <Link
      className="resource-list-item table-list-item"
      to={getLink(table, logging)}
      onClick={(e) =>
        logClick(e, {
          target_id: 'table_list_item',
          value: logging.source,
          position: logging.index.toString(),
        })
      }
    >
      <div className="resource-info">
        <span className={generateResourceIconClass(table.database)} />
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
              resourceType={ResourceType.table}
            />
          </div>
          <span className="description-section">
            {table.description && (
              <div
                className="description text-body-w3 truncated"
                dangerouslySetInnerHTML={{
                  __html: tableHighlights.description,
                }}
              />
            )}
          </span>
          {tableHighlights.columns && (
            <MetadataHighlightList
              fieldName="columns"
              highlightedMetadataList={tableHighlights.columns}
            />
          )}
          {tableHighlights.columnDescriptions && (
            <MetadataHighlightList
              fieldName="column description"
              highlightedMetadataList={tableHighlights.columnDescriptions}
            />
          )}
        </div>
      </div>
      <div className="resource-type resource-source">
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
export default TableListItem;
