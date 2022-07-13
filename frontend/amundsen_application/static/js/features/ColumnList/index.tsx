// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as ReactMarkdown from 'react-markdown';
import { OverlayTrigger, Popover } from 'react-bootstrap';

import Table, {
  TableColumn as ReusableTableColumn,
  TextAlignmentValues,
} from 'components/Table';
import {
  getMaxNestedColumns,
  getTableSortCriterias,
} from 'config/config-utils';

import BadgeList from 'features/BadgeList';

import {
  TableColumn,
  SortCriteria,
  SortDirection,
  IconSizes,
  TypeMetadata,
} from 'interfaces';
import { FormattedDataType, ContentType } from 'interfaces/ColumnList';
import { logAction } from 'utils/analytics';
import { buildTableKey, TablePageParams } from 'utils/navigationUtils';

import { GraphIcon } from 'components/SVGIcons/GraphIcon';

import ColumnType from './ColumnType';
import {
  BLOCKQUOTE_MARKDOWN_TYPE,
  EMPTY_MESSAGE,
  HAS_COLUMN_STATS_TEXT,
  LIST_MARKDOWN_TYPE,
} from './constants';

import './styles.scss';

export interface ComponentProps {
  columns: TableColumn[];
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
  areNestedColumnsExpanded: boolean | undefined;
  toggleExpandingColumns: () => void;
  hasColumnsToExpand: () => boolean;
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

const hasTypeMetadataWithBadge = (typeMetadata: TypeMetadata[]) =>
  typeMetadata.some((tm) => {
    if (tm.badges?.length) {
      return true;
    }
    return hasTypeMetadataWithBadge(tm.children || []);
  });

const hasColumnWithBadge = (columns: TableColumn[]) =>
  columns.some((col) => {
    if (col.badges?.length) {
      return true;
    }
    return (
      col.type_metadata?.badges?.length ||
      hasTypeMetadataWithBadge(col.type_metadata?.children || [])
    );
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
  preExpandPanelKey,
  sortBy = DEFAULT_SORTING,
  tableParams,
  preExpandRightPanel,
  toggleRightPanel,
  hideSomeColumnMetadata,
  currentSelectedKey,
  areNestedColumnsExpanded,
  toggleExpandingColumns,
  hasColumnsToExpand,
}: ColumnListProps) => {
  const hasColumnBadges = hasColumnWithBadge(columns);
  const formatColumnData = (item, index) => {
    const hasItemStats = !!item.stats.length;
    return {
      stats: hasItemStats ? item.stats : null,
      content: {
        title: item.name,
        description: item.description,
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
      key: item.key,
      name: item.name,
      isEditable: item.is_editable,
      isExpandable:
        item.type_metadata && item.type_metadata.children.length > 0,
      editText: editText || null,
      editUrl: editUrl || null,
      tableParams,
      index,
      typeMetadata: item.type_metadata,
    };
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

  let tableKey;
  if (orderedData.length) {
    tableKey = buildTableKey(orderedData[0].tableParams);
  }

  let formattedColumns: ReusableTableColumn[] = [
    {
      title: 'Name',
      field: 'content',
      component: (
        { title, description, hasStats }: ContentType,
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

        const handleColumnNameClick = () => {
          toggleRightPanel(columnDetails);
        };

        return (
          <>
            <div className="column-name-container">
              <div className="column-name-with-icons">
                <button
                  className="column-name-button"
                  type="button"
                  onClick={handleColumnNameClick}
                >
                  <h3 className="column-name">{title}</h3>
                </button>
                {columnMetadataIcons}
              </div>
              <ReactMarkdown
                className="column-desc"
                disallowedTypes={[BLOCKQUOTE_MARKDOWN_TYPE, LIST_MARKDOWN_TYPE]}
                unwrapDisallowed
              >
                {description}
              </ReactMarkdown>
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
    key: item.key,
    name: item.name,
    isEditable: item.is_editable,
    isExpandable: item.children?.length > 0,
    editText: editText || null,
    editUrl: editUrl || null,
    tableParams,
    index,
    isNestedColumn: true,
    kind: item.kind,
  });

  return (
    <Table
      columns={formattedColumns}
      data={orderedData}
      options={{
        rowHeight: 72,
        emptyMessage: EMPTY_MESSAGE,
        formatChildrenData: formatNestedColumnData,
        onExpand: handleRowExpand,
        onRowClick: toggleRightPanel,
        tableClassName: 'table-detail-table',
        preExpandRightPanel,
        preExpandPanelKey,
        currentSelectedKey,
        tableKey,
        maxNumRows: getMaxNestedColumns(),
        shouldExpandAllRows: areNestedColumnsExpanded,
        toggleExpandingRows: toggleExpandingColumns,
        hasRowsToExpand: hasColumnsToExpand,
      }}
    />
  );
};

export default ColumnList;
