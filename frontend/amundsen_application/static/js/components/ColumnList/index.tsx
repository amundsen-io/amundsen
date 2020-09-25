// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';

import { OpenRequestAction } from 'ducks/notification/types';

import EditableSection from 'components/common/EditableSection';
import Table, {
  TableColumn as ReusableTableColumn,
} from 'components/common/Table';

import { logAction } from 'ducks/utilMethods';
import { notificationsEnabled, getMaxLength } from 'config/config-utils';
import { TableColumn, RequestMetadataType } from 'interfaces';

import ColumnType from './ColumnType';
import ColumnDescEditableText from './ColumnDescEditableText';
import { getStatsInfoText } from './utils';

import {
  MORE_BUTTON_TEXT,
  REQUEST_DESCRIPTION_TEXT,
  EMPTY_MESSAGE,
  EDITABLE_SECTION_TITLE,
  COLUMN_STATS_TITLE,
} from './constants';

import './styles.scss';

export interface ColumnListProps {
  columns: TableColumn[];
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName: string
  ) => OpenRequestAction;
  database: string;
  editText?: string;
  editUrl?: string;
}

type ContentType = {
  title: string;
  description: string;
};

type DatatypeType = {
  name: string;
  database: string;
  type: string;
};

type StatType = {
  end_epoch: number;
  start_epoch: number;
  stat_type: string;
  stat_val: string;
};

type FormattedDataType = {
  content: ContentType;
  type: DatatypeType;
  usage: string | null;
  stats: StatType | null;
  action: string;
  editText?: string;
  editUrl?: string;
  index: number;
  isEditable: boolean;
};

type ExpandedRowProps = {
  rowValue: FormattedDataType;
  index: number;
};

const SHOW_STATS_THRESHOLD = 1;

const handleRowExpand = (rowValues) => {
  logAction({
    command: 'click',
    label: `${rowValues.content.title} ${rowValues.type.type}`,
    target_id: `column::${rowValues.content.title}`,
    target_type: 'column stats',
  });
};

// @ts-ignore
const ExpandedRowComponent: React.FC<ExpandedRowProps> = (
  rowValue: FormattedDataType
) => {
  const shouldRenderDescription = () => {
    const { content, editText, editUrl, isEditable } = rowValue;

    if (content.description) {
      return true;
    }
    if (!editText && !editUrl && !isEditable) {
      return false;
    }

    return true;
  };

  return (
    <div className="expanded-row-container">
      {shouldRenderDescription() && (
        <EditableSection
          title={EDITABLE_SECTION_TITLE}
          readOnly={!rowValue.isEditable}
          editText={rowValue.editText}
          editUrl={rowValue.editUrl}
        >
          <ColumnDescEditableText
            columnIndex={rowValue.index}
            editable={rowValue.isEditable}
            maxLength={getMaxLength('columnDescLength')}
            value={rowValue.content.description}
          />
        </EditableSection>
      )}
      {rowValue.stats && (
        <div className="stat-collection-info">
          <span className="stat-title">{COLUMN_STATS_TITLE} </span>
          {getStatsInfoText(
            rowValue.stats.start_epoch,
            rowValue.stats.end_epoch
          )}
        </div>
      )}
    </div>
  );
};

const ColumnList: React.FC<ColumnListProps> = ({
  columns,
  database,
  editText,
  editUrl,
  openRequestDescriptionDialog,
}: ColumnListProps) => {
  const formattedData: FormattedDataType[] = columns.map((item, index) => {
    const hasItemStats = !!item.stats.length;

    return {
      content: {
        title: item.name,
        description: item.description,
      },
      type: {
        type: item.col_type,
        name: item.name,
        database,
      },
      usage: hasItemStats ? item.stats[0].stat_val : '',
      stats: hasItemStats ? item.stats[0] : null,
      action: item.name,
      isEditable: item.is_editable,
      editText,
      editUrl,
      index,
    };
  });
  const statsCount = formattedData.filter((item) => !!item.stats).length;
  const hasStats = statsCount >= SHOW_STATS_THRESHOLD;

  let formattedColumns: ReusableTableColumn[] = [
    {
      title: 'Name',
      field: 'content',
      component: ({ title, description }: ContentType) => (
        <>
          <div className="column-name">{title}</div>
          <div className="column-desc truncated">{description}</div>
        </>
      ),
    },
    {
      title: 'Type',
      field: 'type',
      component: (type) => (
        <div className="resource-type">
          <ColumnType
            type={type.type}
            database={type.database}
            columnName={type.name}
          />
        </div>
      ),
    },
  ];

  if (hasStats) {
    formattedColumns = [
      ...formattedColumns,
      {
        title: 'Usage',
        field: 'usage',
        horAlign: 'right',
        component: (usage) => (
          <p className="resource-type usage-value">{usage}</p>
        ),
      },
    ];
  }

  if (notificationsEnabled()) {
    formattedColumns = [
      ...formattedColumns,
      {
        title: '',
        field: 'action',
        width: 80,
        horAlign: 'right',
        component: (name, index) => (
          <div className="actions">
            <Dropdown
              id={`detail-list-item-dropdown:${index}`}
              pullRight
              className="column-dropdown"
            >
              <Dropdown.Toggle noCaret>
                <span className="sr-only">{MORE_BUTTON_TEXT}</span>
                <img className="icon icon-more" alt="" />
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <MenuItem
                  onClick={() => {
                    openRequestDescriptionDialog(
                      RequestMetadataType.COLUMN_DESCRIPTION,
                      name
                    );
                  }}
                >
                  {REQUEST_DESCRIPTION_TEXT}
                </MenuItem>
              </Dropdown.Menu>
            </Dropdown>
          </div>
        ),
      },
    ];
  }

  return (
    <Table
      columns={formattedColumns}
      data={formattedData}
      options={{
        rowHeight: 72,
        emptyMessage: EMPTY_MESSAGE,
        expandRow: ExpandedRowComponent,
        onExpand: handleRowExpand,
        tableClassName: 'table-detail-table',
      }}
    />
  );
};

export default ColumnList;
