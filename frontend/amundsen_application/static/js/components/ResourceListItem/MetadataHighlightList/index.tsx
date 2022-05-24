// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { TableIcon } from 'components/SVGIcons';
import { IconSizes } from 'interfaces';
import { CodeIcon } from 'components/SVGIcons/CodeIcon';
import { ChartIcon } from 'components/SVGIcons/ChartIcon';

export interface MetadataHighlightListProps {
  fieldName: string;
  highlightedMetadataList: string;
}

const getIcon = (fieldName: string) => {
  if (fieldName.includes('chart')) {
    return <ChartIcon size={IconSizes.SMALL} />;
  }
  if (fieldName.includes('query')) {
    return <CodeIcon size={IconSizes.SMALL} />;
  }

  return <TableIcon size={IconSizes.SMALL} />;
};

const MetadataHighlightList: React.FC<MetadataHighlightListProps> = ({
  fieldName,
  highlightedMetadataList,
}) => (
  <div className="metadata-highlight-list">
    <div className="highlight-icon">{getIcon(fieldName)}</div>
    <div
      className="highlight-content body-secondary-3 truncated"
      dangerouslySetInnerHTML={{
        __html: `<span class='section-title'>Matching ${fieldName}:</span> ${highlightedMetadataList}`,
      }}
    />
  </div>
);
export default MetadataHighlightList;
