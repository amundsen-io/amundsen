// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import './styles.scss';

import { ResourceType } from 'interfaces';
import {
  RESOURCE_HEADER_TITLE,
  SOURCE_HEADER_TITLE,
  BADGES_HEADER_TITLE,
  LAST_UPDATED_HEADER_TITLE,
  ENTITY_HEADER_TITLE,
} from './constants';

export interface ResourceListHeaderProps {
  resourceTypes: ResourceType[];
}

const getResourceHeaders = (type: ResourceType) => {
  switch (type) {
    case ResourceType.dashboard:
      return [
        RESOURCE_HEADER_TITLE,
        SOURCE_HEADER_TITLE,
        LAST_UPDATED_HEADER_TITLE,
      ];
    case ResourceType.feature:
      return [
        RESOURCE_HEADER_TITLE,
        SOURCE_HEADER_TITLE,
        BADGES_HEADER_TITLE,
        ENTITY_HEADER_TITLE,
      ];
    case ResourceType.table:
      return [RESOURCE_HEADER_TITLE, SOURCE_HEADER_TITLE, BADGES_HEADER_TITLE];
    case ResourceType.user:
      return [RESOURCE_HEADER_TITLE, SOURCE_HEADER_TITLE, BADGES_HEADER_TITLE];
  }
};

const ResourceListHeader: React.FC<ResourceListHeaderProps> = ({
  resourceTypes,
}: ResourceListHeaderProps) => {
  const headers = getResourceHeaders(resourceTypes[0]);
  return (
    <div className="resource-list-header">
      {headers?.map((headerText, index) => {
        return (
          <span className={`header-${index}`} key={`header-${index}`}>
            <span className="header-text">{headerText}</span>
          </span>
        );
      })}
    </div>
  );
};

export default ResourceListHeader;
