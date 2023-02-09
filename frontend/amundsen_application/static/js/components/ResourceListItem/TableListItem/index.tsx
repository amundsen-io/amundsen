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
  disabled?: boolean;
}

/*
  this function get's the table name from the key to preserve original
  capitalization since search needs the names to be lowercase for analysis
*/
export const getName = (table) => {
  const splitKey = table.key.split('/');
  const keyName = splitKey[splitKey.length - 1];

  if (keyName.toLowerCase() === table.name) {
    return keyName;
  }

  return table.name;
};

export const getLink = (table, logging) => {
  const name = getName(table);

  if (table.link) return table.link;

  return (
    `/table_detail/${table.cluster}/${table.database}/${table.schema}/${name}` +
    `?index=${logging.index}&source=${logging.source}`
  );
};

export const generateResourceIconClass = (databaseId: string): string =>
  `icon resource-icon ${getSourceIconClass(databaseId, ResourceType.table)}`;

const TableListItem: React.FC<TableListItemProps> = ({
  table,
  logging,
  tableHighlights,
  disabled,
}) => (
  <li className="list-group-item">
    <Link
      className={`resource-list-item table-list-item ${
        disabled ? 'is-disabled' : 'clickable'
      }`}
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
                  table={getName(table)}
                  desc={table.schema_description}
                />
              )}
              {!table.schema_description && `${table.schema}.${getName(table)}`}
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
