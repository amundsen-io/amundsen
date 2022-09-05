// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import { Link } from 'react-router-dom';
import { LoggingParams } from '../types';
import { logClick } from 'utils/analytics';
import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import { ResourceType, ServiceResource } from 'interfaces';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';

export interface ServiceListItemProps {
  service: ServiceResource;
  logging: LoggingParams;
}

export const getLink = (service, logging) =>
  `/service/${service.key}` +
  `?index=${logging.index}&source=${logging.source}`;

export const generateResourceIconClass = (databaseId: string): string =>
  `icon resource-icon ${getSourceIconClass(databaseId, ResourceType.service)}`;

const ServiceListItem: React.FC<ServiceListItemProps> = ({
  service,
  logging,
}) => {
  return (
    <li className="list-group-item clickable">
      <Link
        className="resource-list-item table-list-item"
        to={getLink(service, logging)}
        onClick={(e) =>
          logClick(e, { target_id: 'table_list_item', value: logging.source })
        }
      >
        <div className="resource-info">
          <span className={generateResourceIconClass(service.name)} />
          <div className="resource-info-text my-auto">
            <div className="resource-name">
              <div className="truncated">
                {service.description && (
                  <SchemaInfo
                    schema={'service'}
                    table={service.name}
                    desc={service.description}
                  />
                )}
              </div>
              <BookmarkIcon
              bookmarkKey={service.key}
              resourceType={ResourceType.service}
            />
            </div>
            <div className="body-secondary-3 truncated">
              {service.description}
            </div>
          </div>
        </div>
        <div className="resource-type resource-source">
         {service.criticality}
        </div>
        <div className="resource-badges">
         {service.stack}
        </div>
      </Link>
    </li>
  );
};

export default ServiceListItem;
