// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import EditableSection from 'components/EditableSection';
import BadgeList from 'features/BadgeList';
import ColumnDescEditableText from 'features/ColumnList/ColumnDescEditableText';
import ColumnLineage from 'features/ColumnList/ColumnLineage';
import ColumnStats from 'features/ColumnList/ColumnStats';
import ExpandableUniqueValues from 'features/ExpandableUniqueValues';
import { getMaxLength, isColumnListLineageEnabled } from 'config/config-utils';
import { getColumnLink } from 'utils/navigationUtils';
import { filterOutUniqueValues, getUniqueValues } from 'utils/stats';
import { FormattedDataType } from '..';
import {
  COPY_COL_LINK_LABEL,
  COPY_COL_NAME_LABEL,
  EDITABLE_SECTION_TITLE,
  CLOSE_LABEL,
} from './constants';

export interface ColumnDetailsPanelProps {
  columnDetails: FormattedDataType;
  togglePanel: (
    columnDetails: FormattedDataType | undefined,
    event: any
  ) => void;
}

const shouldRenderDescription = (columnDetails: FormattedDataType) => {
  const { content, editText, editUrl, isEditable } = columnDetails;
  if (content.description) {
    return true;
  }
  if (!editText && !editUrl && !isEditable) {
    return false;
  }
  return true;
};

const ColumnDetailsPanel: React.FC<ColumnDetailsPanelProps> = ({
  columnDetails,
  togglePanel,
}: ColumnDetailsPanelProps) => {
  const {
    content,
    stats,
    editText,
    editUrl,
    col_index,
    name,
    tableParams,
    isEditable,
    badges,
  } = columnDetails;

  const normalStats = stats && filterOutUniqueValues(stats);
  const uniqueValueStats = stats && getUniqueValues(stats);

  const handleCloseButtonClick = (e) => {
    togglePanel(undefined, e);
  };

  const handleCopyNameClick = () => {
    navigator.clipboard.writeText(name);
  };

  const handleCopyLinkClick = () => {
    navigator.clipboard.writeText(getColumnLink(tableParams, name));
  };

  return (
    <aside className="right-panel">
      <div className="panel-header">
        <h2 className="panel-title">{name}</h2>
        <button
          type="button"
          className="btn btn-close"
          onClick={handleCloseButtonClick}
        >
          <span className="sr-only">{CLOSE_LABEL}</span>
        </button>
      </div>
      <div className="buttons-row">
        <button
          className="btn btn-default column-button"
          id="copy-col-name"
          type="button"
          onClick={handleCopyNameClick}
        >
          {COPY_COL_NAME_LABEL}
        </button>
        <button
          className="btn btn-default"
          id="copy-col-link"
          type="button"
          onClick={handleCopyLinkClick}
        >
          {COPY_COL_LINK_LABEL}
        </button>
      </div>
      {badges.length > 0 && (
        <div className="metadata-section">
          <BadgeList badges={badges} />
        </div>
      )}
      {shouldRenderDescription(columnDetails) && (
        <EditableSection
          title={EDITABLE_SECTION_TITLE}
          readOnly={!isEditable}
          editText={editText || undefined}
          editUrl={editUrl || undefined}
        >
          <ColumnDescEditableText
            columnIndex={col_index}
            editable={isEditable}
            maxLength={getMaxLength('columnDescLength')}
            value={content.description}
          />
        </EditableSection>
      )}
      {normalStats && normalStats.length > 0 && (
        <div className="metadata-section">
          <ColumnStats stats={normalStats} singleColumnDisplay />
        </div>
      )}
      {uniqueValueStats && uniqueValueStats.length > 0 && (
        <div className="metadata-section">
          <ExpandableUniqueValues uniqueValues={uniqueValueStats} />
        </div>
      )}
      {isColumnListLineageEnabled() && (
        <div className="metadata-section">
          <ColumnLineage columnName={name} singleColumnDisplay />
        </div>
      )}
    </aside>
  );
};

export default ColumnDetailsPanel;
