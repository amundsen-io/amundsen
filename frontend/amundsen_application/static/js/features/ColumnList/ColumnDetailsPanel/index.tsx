// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import EditableSection from 'components/EditableSection';
import BadgeList from 'features/BadgeList';
import ColumnDescEditableText from 'features/ColumnList/ColumnDescEditableText';
import ColumnLineage from 'features/ColumnList/ColumnLineage';
import ColumnStats from 'features/ColumnList/ColumnStats';
import ExpandableUniqueValues from 'features/ExpandableUniqueValues';
import { FormattedDataType } from 'interfaces/ColumnList';
import RequestDescriptionText from 'pages/TableDetailPage/RequestDescriptionText';
import {
  getMaxLength,
  isColumnListLineageEnabled,
  notificationsEnabled,
} from 'config/config-utils';
import { buildTableKey, getColumnLink } from 'utils/navigationUtils';
import { filterOutUniqueValues, getUniqueValues } from 'utils/stats';
import { RequestMetadataType } from 'interfaces/Notifications';
import {
  COPY_COL_LINK_LABEL,
  COPY_COL_NAME_LABEL,
  EDITABLE_SECTION_TITLE,
  CLOSE_LABEL,
} from './constants';

export interface ColumnDetailsPanelProps {
  columnDetails: FormattedDataType;
  togglePanel: (columnDetails: FormattedDataType | undefined) => void;
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

const getColumnNamePath = (key, tableParams) => {
  const tableKey = buildTableKey(tableParams);
  const columnNamePath = key.replace(tableKey + '/', '');
  return columnNamePath;
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
    key,
    name,
    tableParams,
    isEditable,
    badges,
    isNestedColumn,
  } = columnDetails;

  const normalStats = stats && filterOutUniqueValues(stats);
  const uniqueValueStats = stats && getUniqueValues(stats);

  const handleCloseButtonClick = () => {
    togglePanel(undefined);
  };

  const handleCopyNameClick = () => {
    navigator.clipboard.writeText(getColumnNamePath(key, tableParams));
  };

  const handleCopyLinkClick = () => {
    navigator.clipboard.writeText(
      getColumnLink(tableParams, getColumnNamePath(key, tableParams))
    );
  };

  return (
    <aside className="right-panel">
      <div className="panel-header">
        <h2 className="panel-title">{content.title}</h2>
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
            columnKey={key}
            isNestedColumn={isNestedColumn || false}
            editable={isEditable}
            maxLength={getMaxLength('columnDescLength')}
            value={content.description}
          />
          <span>
            {notificationsEnabled() && (
              <RequestDescriptionText
                requestMetadataType={RequestMetadataType.COLUMN_DESCRIPTION}
                columnName={getColumnNamePath(key, tableParams)}
              />
            )}
          </span>
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
