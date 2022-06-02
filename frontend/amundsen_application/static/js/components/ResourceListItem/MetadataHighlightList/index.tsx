// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { TableIcon } from 'components/SVGIcons';
import { IconSizes } from 'interfaces';
import { CodeIcon } from 'components/SVGIcons/CodeIcon';
import { ChartIcon } from 'components/SVGIcons/ChartIcon';

const CHART_SUBSTR = 'chart';
const QUERY_SUBSTR = 'query';

export interface MetadataHighlightListProps {
  fieldName: string;
  highlightedMetadataList: string;
}

const getIcon = (fieldName: string) => {
  if (fieldName.includes(CHART_SUBSTR)) {
    return <ChartIcon size={IconSizes.SMALL} />;
  }
  if (fieldName.includes(QUERY_SUBSTR)) {
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
      className="highlight-content text-body-w3 truncated"
      dangerouslySetInnerHTML={{
        __html: `<span class='text-title-w3'>Matching ${fieldName}:</span> ${highlightedMetadataList}`,
      }}
    />
  </div>
);
export default MetadataHighlightList;
