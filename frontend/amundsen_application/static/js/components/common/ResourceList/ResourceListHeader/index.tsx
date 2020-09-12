// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import './styles.scss';

import {
  RESOURCE_HEADER_TITLE,
  SOURCE_HEADER_TITLE,
  BADGES_HEADER_TITLE,
} from './constants';

const ResourceListHeader: React.FC = () => {
  return (
    <div className="resource-list-header">
      <span className="resource">
        <span className="resource-text">{RESOURCE_HEADER_TITLE}</span>
      </span>
      <span className="source">{SOURCE_HEADER_TITLE}</span>
      <span className="badges">
        <span className="badges-text">{BADGES_HEADER_TITLE}</span>
      </span>
    </div>
  );
};

export default ResourceListHeader;
