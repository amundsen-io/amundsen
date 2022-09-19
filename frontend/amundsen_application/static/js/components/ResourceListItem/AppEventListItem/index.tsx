// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import { Link } from 'react-router-dom';
import { logClick } from 'utils/analytics';
import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import { AppEventResource, ResourceType } from 'interfaces';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';
import { LoggingParams } from '../types';

export interface AppEventListItemProps {
  appEvent: AppEventResource;
  logging: LoggingParams;
}

export const getLink = (event, logging) =>
  `/events/${event?.key}` +
  `?index=${logging?.index}&source=${logging?.source}`;

export const generateResourceIconClass = (databaseId: string): string =>
  `icon resource-icon ${getSourceIconClass(databaseId, ResourceType.events)}`;

const AppEventListItem: React.FC<AppEventListItemProps> = ({
  appEvent,
  logging,
}) => (
  <li className="list-group-item clickable">
    <Link
      className="resource-list-item table-list-item"
      to={getLink(appEvent, logging)}
      onClick={(e) =>
        logClick(e, { target_id: 'table_list_item', value: logging.source })
      }
    >
      <div className="resource-info">
        <span className={generateResourceIconClass(appEvent.name)} />
        <div className="resource-info-text my-auto">
          <div className="resource-name">
            <div className="truncated">
              {appEvent.description && (
                <SchemaInfo
                  schema="events"
                  table={appEvent.name}
                  desc={appEvent.description}
                />
              )}
            </div>
            <BookmarkIcon
              bookmarkKey={appEvent.key}
              resourceType={ResourceType.events}
            />
          </div>
          <div className="body-secondary-3 truncated">
            {appEvent.description}
          </div>
        </div>
      </div>
      <div className="resource-type resource-source">{appEvent.source}</div>
      <div className="resource-badges">{appEvent.vertical}</div>
    </Link>
  </li>
);

export default AppEventListItem;
