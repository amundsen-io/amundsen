// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { TableIcon } from 'components/SVGIcons';
import { DashboardSearchHighlights, IconSizes, TableSearchHighlights } from 'interfaces';

export interface MetadataHighlightListProps {
  fieldName: string;
  highlightedMetadata: TableSearchHighlights | DashboardSearchHighlights;
}
// TODO add icons mapping for columns, charts, queries

// const fieldToIconMapping = {
//   columns:  
// }

// const formatHighlightedItemList = (fieldName, highlightedItems): string => {
//   const formatted = ;
//   return formatted;
// }

const getHighlightedMetadata = ({fieldName, highlightedMetadata}: MetadataHighlightListProps): string[] => {
  const highlightedItems = highlightedMetadata[fieldName]? highlightedMetadata[fieldName] : [];
  return highlightedItems.join(', ');

}

const MetadataHighlightList: React.FC<MetadataHighlightListProps> = ({ fieldName, highlightedMetadata }) => (
  <div className='metadata-highlight-list'>
    <div className='highlight-icon'><TableIcon size={IconSizes.SMALL}/></div>
    <div
    className='highlight-content body-secondary-3 truncated'
    dangerouslySetInnerHTML={{
      __html: `<span class='section-title'>Matching ${fieldName}:</span> ${getHighlightedMetadata({fieldName, highlightedMetadata})}`
      }}>
    </div>
  </div>
);
export default MetadataHighlightList;
