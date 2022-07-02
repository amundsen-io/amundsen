// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { OverlayTrigger, Popover } from 'react-bootstrap';
import EditableSection from 'components/EditableSection';
import BadgeList from 'features/BadgeList';
import ColumnDescEditableText from 'features/ColumnList/ColumnDescEditableText';
import ColumnLineage from 'features/ColumnList/ColumnLineage';
import ColumnType from 'features/ColumnList/ColumnType';
import ColumnStats from 'features/ColumnList/ColumnStats';
import ExpandableUniqueValues from 'features/ExpandableUniqueValues';
import { FormattedDataType } from 'interfaces/ColumnList';
import { RequestMetadataType } from 'interfaces/Notifications';
import RequestDescriptionText from 'pages/TableDetailPage/RequestDescriptionText';
import {
  getMaxLength,
  isColumnListLineageEnabled,
  notificationsEnabled,
} from 'config/config-utils';
import { buildTableKey, getColumnLink } from 'utils/navigationUtils';
import { filterOutUniqueValues, getUniqueValues } from 'utils/stats';
import {
  COPY_COL_LINK_LABEL,
  COPY_COL_NAME_LABEL,
  COPIED_TO_CLIPBOARD_TEXT,
  EDITABLE_SECTION_TITLE,
  CLOSE_LABEL,
  TYPE_SECTION_TITLE,
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
    type,
    editText,
    editUrl,
    key,
    name,
    tableParams,
    isEditable,
    badges,
    isNestedColumn,
  } = columnDetails;

  const panelRef = React.useRef<HTMLButtonElement>(null);
  React.useEffect(() => {
    if (panelRef.current !== null) {
      panelRef.current.focus();
    }
  });

  const normalStats = stats && filterOutUniqueValues(stats);
  const uniqueValueStats = stats && getUniqueValues(stats);
  const copiedToClipboardPopover = (
    <Popover id="popover-click">{COPIED_TO_CLIPBOARD_TEXT}</Popover>
  );

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
          ref={panelRef}
        >
          <span className="sr-only">{CLOSE_LABEL}</span>
        </button>
      </div>
      <div className="buttons-row">
        <OverlayTrigger
          key="copy-col-name"
          trigger="click"
          rootClose
          placement="top"
          overlay={copiedToClipboardPopover}
        >
          <button
            className="btn btn-default column-button"
            id="copy-col-name"
            type="button"
            onClick={handleCopyNameClick}
          >
            {COPY_COL_NAME_LABEL}
          </button>
        </OverlayTrigger>
        <OverlayTrigger
          key="copy-col-link"
          trigger="click"
          rootClose
          placement="top"
          overlay={copiedToClipboardPopover}
        >
          <button
            className="btn btn-default"
            id="copy-col-link"
            type="button"
            onClick={handleCopyLinkClick}
          >
            {COPY_COL_LINK_LABEL}
          </button>
        </OverlayTrigger>
      </div>
      {badges.length > 0 && (
        <div className="metadata-section">
          <BadgeList badges={badges} />
        </div>
      )}
      <div className="metadata-section">
        <h3 className="section-title">{TYPE_SECTION_TITLE}</h3>
        <ColumnType
          type={type.type}
          database={type.database}
          columnName={type.name}
        />
      </div>
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
