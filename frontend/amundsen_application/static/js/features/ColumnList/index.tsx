// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';

import { NestingArrow } from 'components/SVGIcons/NestingArrow';
import Table, {
  TableColumn as ReusableTableColumn,
  TextAlignmentValues,
} from 'components/Table';
import {
  getMaxNestedColumns,
  getTableSortCriterias,
  notificationsEnabled,
} from 'config/config-utils';

import { OpenRequestAction } from 'ducks/notification/types';
import { getColumnCount } from 'ducks/tableMetadata/api/helpers';

import BadgeList from 'features/BadgeList';

import {
  TableColumn,
  RequestMetadataType,
  SortCriteria,
  SortDirection,
  IconSizes,
} from 'interfaces';
import { FormattedDataType, ContentType } from 'interfaces/ColumnList';
import { logAction } from 'utils/analytics';
import {
  buildTableKey,
  getColumnLink,
  TablePageParams,
} from 'utils/navigationUtils';

import { GraphIcon } from 'components/SVGIcons/GraphIcon';

import ColumnType from './ColumnType';
import {
  MORE_BUTTON_TEXT,
  REQUEST_DESCRIPTION_TEXT,
  EMPTY_MESSAGE,
  COPY_COLUMN_LINK_TEXT,
  HAS_COLUMN_STATS_TEXT,
} from './constants';

import './styles.scss';

export interface ComponentProps {
  columns: TableColumn[];
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName: string
  ) => OpenRequestAction;
  database: string;
  editText?: string;
  editUrl?: string;
  preExpandPanelKey?: string;
  sortBy?: SortCriteria;
  tableParams: TablePageParams;
  preExpandRightPanel: (columnDetails: FormattedDataType) => void;
  toggleRightPanel: (newColumnDetails: FormattedDataType | undefined) => void;
  hideSomeColumnMetadata: boolean;
  currentSelectedKey: string;
}

export type ColumnListProps = ComponentProps;

// TODO: Move this into the configuration once we have more info about the rest of stats
const USAGE_STAT_TYPE = 'column_usage';
const SHOW_STATS_THRESHOLD = 1;
const DEFAULT_SORTING: SortCriteria = {
  name: 'Table Default',
  key: 'sort_order',
  direction: SortDirection.ascending,
};

const getSortingFunction = (
  formattedData: FormattedDataType[],
  sortBy: SortCriteria
) => {
  const numberSortingFunction = (a, b) => b[sortBy.key] - a[sortBy.key];

  const stringSortingFunction = (a, b) => {
    if (a[sortBy.key] && b[sortBy.key]) {
      return a[sortBy.key].localeCompare(b[sortBy.key]);
    }
    return null;
  };

  if (!formattedData.length) {
    return numberSortingFunction;
  }

  return Number.isInteger(formattedData[0][sortBy.key])
    ? numberSortingFunction
    : stringSortingFunction;
};

const hasColumnWithBadge = (columns: TableColumn[]) =>
  columns.some((col) => {
    if (col.badges) {
      return col.badges.length > 0;
    }
    return false;
  });

const getUsageStat = (item) => {
  const hasItemStats = !!item.stats.length;

  if (hasItemStats) {
    const usageStat = item.stats.find((s) => s.stat_type === USAGE_STAT_TYPE);

    return usageStat ? +usageStat.stat_val : null;
  }

  return null;
};

const getColumnMetadataIconElement = (key, popoverText, iconElement) => (
  <OverlayTrigger
    key={key}
    trigger={['hover', 'focus']}
    placement="top"
    overlay={<Popover id="popover-trigger-hover-focus">{popoverText}</Popover>}
  >
    <span>{iconElement}</span>
  </OverlayTrigger>
);

const ColumnList: React.FC<ColumnListProps> = ({
  columns,
  database,
  editText,
  editUrl,
  openRequestDescriptionDialog,
  preExpandPanelKey,
  sortBy = DEFAULT_SORTING,
  tableParams,
  preExpandRightPanel,
  toggleRightPanel,
  hideSomeColumnMetadata,
  currentSelectedKey,
}: ColumnListProps) => {
  const hasColumnBadges = hasColumnWithBadge(columns);
  const formatColumnData = (item, index) => {
    const hasItemStats = !!item.stats.length;
    return {
      stats: hasItemStats ? item.stats : null,
      content: {
        title: item.name,
        description: item.description,
        nestedLevel: item.nested_level || 0,
        hasStats: hasItemStats,
      },
      type: {
        type: item.col_type,
        name: item.name,
        database,
      },
      children: item.children || [],
      sort_order: item.sort_order,
      usage: getUsageStat(item),
      badges: hasColumnBadges ? item.badges : [],
      action: {
        isActionEnabled: !item.nested_level,
      },
      key: item.key,
      name: item.name,
      isEditable: item.is_editable,
      isExpandable: false,
      editText: editText || null,
      editUrl: editUrl || null,
      tableParams,
      index,
      typeMetadata: item.type_metadata,
    };
  };
  const hideNestedColumns = React.useMemo(
    () => getColumnCount(columns) >= getMaxNestedColumns(),
    [columns]
  );
  const flattenData = (orderedData: FormattedDataType[]) => {
    const data: FormattedDataType[] = [];
    orderedData.forEach((item) => {
      data.push(item);
      if (item.children !== undefined) {
        data.push(...item.children.map(formatColumnData));
      }
    });
    return data;
  };
  const formattedData: FormattedDataType[] = columns.map(formatColumnData);
  const statsCount = formattedData.filter((item) => !!item.stats).length;
  const hasUsageStat =
    getTableSortCriterias().usage && statsCount >= SHOW_STATS_THRESHOLD;
  let orderedData = formattedData.sort(
    getSortingFunction(formattedData, sortBy)
  );
  if (sortBy.direction === SortDirection.ascending) {
    orderedData = orderedData.reverse();
  }
  const flattenedData: FormattedDataType[] = hideNestedColumns
    ? orderedData
    : flattenData(orderedData);

  let tableKey;
  if (flattenedData.length) {
    tableKey = buildTableKey(flattenedData[0].tableParams);
  }

  let formattedColumns: ReusableTableColumn[] = [
    {
      title: 'Name',
      field: 'content',
      component: (
        { title, description, nestedLevel, hasStats }: ContentType,
        index,
        columnDetails: FormattedDataType
      ) => {
        let columnMetadataIcons: React.ReactNode[] = [];
        if (hasStats) {
          const hasStatsIcon = getColumnMetadataIconElement(
            'has-stats',
            HAS_COLUMN_STATS_TEXT,
            <GraphIcon size={IconSizes.SMALL} />
          );
          columnMetadataIcons = [...columnMetadataIcons, hasStatsIcon];
        }

        const isFrontendParsedNestedColumn =
          nestedLevel !== undefined && nestedLevel > 0;
        const handleColumnNameClick = () => {
          toggleRightPanel(columnDetails);
        };

        return (
          <>
            {isFrontendParsedNestedColumn && (
              <>
                <span
                  className={`nesting-arrow-spacer spacer-${nestedLevel}`}
                />
                <NestingArrow />
              </>
            )}
            <div className="column-name-container">
              <div className="column-name-with-icons">
                {isFrontendParsedNestedColumn ? (
                  <h3 className="column-name text-primary">{title}</h3>
                ) : (
                  <button
                    className="column-name-button"
                    type="button"
                    onClick={handleColumnNameClick}
                  >
                    <h3 className="column-name">{title}</h3>
                  </button>
                )}
                {columnMetadataIcons}
              </div>
              <p className="column-desc truncated">{description}</p>
            </div>
          </>
        );
      },
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

  if (hasUsageStat && !hideSomeColumnMetadata) {
    formattedColumns = [
      ...formattedColumns,
      {
        title: 'Usage',
        field: 'usage',
        horAlign: TextAlignmentValues.right,
        component: (usage) => (
          <p className="resource-type usage-value">{usage}</p>
        ),
      },
    ];
  }

  if (hasColumnBadges && !hideSomeColumnMetadata) {
    formattedColumns = [
      ...formattedColumns,
      {
        title: 'Badges',
        field: 'badges',
        horAlign: TextAlignmentValues.left,
        component: (values) => <BadgeList badges={values} />,
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
        horAlign: TextAlignmentValues.right,
        component: (
          { isActionEnabled },
          index,
          columnDetails: FormattedDataType
        ) => {
          if (!isActionEnabled) {
            return null;
          }

          const handleCopyLinkClick = () => {
            const tableKey = buildTableKey(tableParams);
            const columnNamePath = columnDetails.key.replace(
              tableKey + '/',
              ''
            );
            navigator.clipboard.writeText(
              getColumnLink(tableParams, columnNamePath)
            );
          };

          return (
            <div className="actions">
              <Dropdown
                id={`detail-list-item-dropdown:${index}`}
                pullRight
                className="column-dropdown"
              >
                <Dropdown.Toggle
                  className={`${
                    columnDetails.isNestedColumn ? 'is-nested-column-row' : ''
                  }`}
                  noCaret
                >
                  <span className="sr-only">{MORE_BUTTON_TEXT}</span>
                  <img className="icon icon-more" alt="" />
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <MenuItem
                    onClick={() => {
                      openRequestDescriptionDialog(
                        RequestMetadataType.COLUMN_DESCRIPTION,
                        columnDetails.key
                      );
                    }}
                  >
                    {REQUEST_DESCRIPTION_TEXT}
                  </MenuItem>
                  <MenuItem onClick={handleCopyLinkClick}>
                    {COPY_COLUMN_LINK_TEXT}
                  </MenuItem>
                </Dropdown.Menu>
              </Dropdown>
            </div>
          );
        },
      },
    ];
  }

  const openedColumnsMap = {};
  const handleRowExpand = (rowValues) => {
    if (openedColumnsMap[rowValues.key]) {
      return;
    }
    openedColumnsMap[rowValues.key] = true;
    logAction({
      command: 'click',
      label: `${rowValues.key} ${rowValues.type.type}`,
      target_id: `column::${rowValues.key}`,
      target_type: 'expand nested columns',
    });
  };

  const formatNestedColumnData = (item, index) => ({
    stats: null,
    content: {
      title: item.name,
      description: item.description,
      hasStats: false,
    },
    type: {
      type: item.data_type,
      name: item.name,
      database,
    },
    children: item.children || [],
    sort_order: item.sort_order,
    usage: null,
    badges: item.badges,
    action: {
      isActionEnabled: true,
    },
    key: item.key,
    name: item.name,
    isEditable: false,
    isExpandable: item.children?.length > 0,
    editText: null,
    editUrl: null,
    tableParams,
    index,
    isNestedColumn: true,
    kind: item.kind,
  });

  return (
    <Table
      columns={formattedColumns}
      data={flattenedData}
      options={{
        rowHeight: 72,
        emptyMessage: EMPTY_MESSAGE,
        formatChildrenData: formatNestedColumnData,
        onExpand: handleRowExpand,
        tableClassName: 'table-detail-table',
        preExpandRightPanel,
        preExpandPanelKey,
        currentSelectedKey,
        tableKey,
        maxNumRows: getMaxNestedColumns(),
      }}
    />
  );
};

export default ColumnList;
