// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import EditableSection from 'components/EditableSection';
import { NestingArrow } from 'components/SVGIcons/NestingArrow';
import Table, {
  TableColumn as ReusableTableColumn,
  TextAlignmentValues,
} from 'components/Table';
import { TAB_URL_PARAM } from 'components/TabsComponent/constants';
import {
  getMaxLength,
  getMaxNestedColumns,
  getTableSortCriterias,
  isColumnListLineageEnabled,
  notificationsEnabled,
} from 'config/config-utils';

import { getTableColumnLineage } from 'ducks/lineage/reducer';
import { GetTableColumnLineageRequest } from 'ducks/lineage/types';
import { OpenRequestAction } from 'ducks/notification/types';
import { getColumnCount } from 'ducks/tableMetadata/api/helpers';

import ExpandableUniqueValues from 'features/ExpandableUniqueValues';
import BadgeList from 'features/BadgeList';
import ColumnLineage from 'features/ColumnList/ColumnLineage';

import {
  TableColumn,
  TableColumnStats,
  RequestMetadataType,
  SortCriteria,
  SortDirection,
  Badge,
} from 'interfaces';
import { TABLE_TAB } from 'pages/TableDetailPage/constants';
import { logAction } from 'utils/analytics';
import { buildTableKey, TablePageParams } from 'utils/navigationUtils';
import { getUniqueValues, filterOutUniqueValues } from 'utils/stats';

import { GraphIcon } from 'components/SVGIcons/GraphIcon';

import ColumnType from './ColumnType';
import ColumnDescEditableText from './ColumnDescEditableText';
import ColumnStats from './ColumnStats';
import {
  MORE_BUTTON_TEXT,
  REQUEST_DESCRIPTION_TEXT,
  EMPTY_MESSAGE,
  EDITABLE_SECTION_TITLE,
  COPY_COLUMN_LINK_TEXT,
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
  selectedColumn?: string;
  sortBy?: SortCriteria;
  tableParams: TablePageParams;
}

export interface DispatchFromProps {
  getColumnLineageDispatch: (
    key: string,
    columnName: string
  ) => GetTableColumnLineageRequest;
}

export type ColumnListProps = ComponentProps & DispatchFromProps;

type ContentType = {
  title: string;
  description: string;
  nestedLevel: number;
};

type DatatypeType = {
  name: string;
  database: string;
  type: string;
};

type ActionType = {
  name: string;
  isActionEnabled: boolean;
};

type FormattedDataType = {
  content: ContentType;
  type: DatatypeType;
  usage: number | null;
  stats: TableColumnStats[] | null;
  children?: TableColumn[];
  action: ActionType;
  editText: string | null;
  editUrl: string | null;
  col_index: number;
  index: number;
  name: string;
  tableParams: TablePageParams;
  sort_order: number;
  isEditable: boolean;
  isExpandable: boolean;
  badges: Badge[];
};

type ExpandedRowProps = {
  rowValue: FormattedDataType;
  index: number;
};

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

const getColumnLink = (tableParams: TablePageParams, columnName: string) => {
  const { cluster, database, schema, table } = tableParams;
  return (
    window.location.origin +
    `/table_detail/${cluster}/${database}/${schema}/${table}` +
    `?${TAB_URL_PARAM}=${TABLE_TAB.COLUMN}&column=${columnName}`
  );
};

// @ts-ignore
const ExpandedRowComponent: React.FC<ExpandedRowProps> = (
  rowValue: FormattedDataType
) => {
  if (!rowValue.isExpandable) {
    return;
  }
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
  const normalStats = rowValue.stats && filterOutUniqueValues(rowValue.stats);
  const uniqueValueStats = rowValue.stats && getUniqueValues(rowValue.stats);

  return (
    <div className="expanded-row-container">
      {shouldRenderDescription() && (
        <EditableSection
          title={EDITABLE_SECTION_TITLE}
          readOnly={!rowValue.isEditable}
          editText={rowValue.editText || undefined}
          editUrl={rowValue.editUrl || undefined}
        >
          <ColumnDescEditableText
            columnIndex={rowValue.col_index}
            editable={rowValue.isEditable}
            maxLength={getMaxLength('columnDescLength')}
            value={rowValue.content.description}
          />
        </EditableSection>
      )}
      {normalStats && <ColumnStats stats={normalStats} />}
      {uniqueValueStats && (
        <ExpandableUniqueValues uniqueValues={uniqueValueStats} />
      )}
      {isColumnListLineageEnabled() && (
        <ColumnLineage columnName={rowValue.name} />
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
  selectedColumn,
  sortBy = DEFAULT_SORTING,
  tableParams,
  getColumnLineageDispatch,
}: ColumnListProps) => {
  let selectedIndex;
  const hasColumnBadges = hasColumnWithBadge(columns);
  const formatColumnData = (item, index) => {
    const hasItemStats = !!item.stats.length;
    return {
      stats: hasItemStats ? item.stats : null,
      content: {
        title: item.name,
        description: item.description,
        nestedLevel: item.nested_level || 0,
      },
      type: {
        type: item.col_type,
        name: item.name,
        database,
      },
      col_index: item.col_index,
      children: item.children,
      sort_order: item.sort_order,
      usage: getUsageStat(item),
      badges: hasColumnBadges ? item.badges : [],
      action: {
        name: item.name,
        isActionEnabled: !item.nested_level,
      },
      name: item.name,
      isEditable: item.is_editable,
      isExpandable: !item.nested_level,
      editText: editText || null,
      editUrl: editUrl || null,
      tableParams,
      index,
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

  const STATS_COLUMN_WIDTH = 24;

  flattenedData.forEach((item, index) => {
    if (item.name === selectedColumn) {
      selectedIndex = index;
    }
  });

  let formattedColumns: ReusableTableColumn[] = [
    {
      title: '',
      field: 'stats',
      width: STATS_COLUMN_WIDTH,
      horAlign: TextAlignmentValues.left,
      component: (stats) => {
        if (stats != null && stats.length > 0) {
          return <GraphIcon />;
        }
        return null;
      },
    },
    {
      title: 'Name',
      field: 'content',
      component: ({ title, description, nestedLevel }: ContentType) => (
        <>
          {nestedLevel > 0 && (
            <>
              <div className={`nesting-arrow-spacer spacer-${nestedLevel}`} />
              <NestingArrow />
            </>
          )}
          <div className="column-name-container">
            <h3 className="column-name">{title}</h3>
            <p className="column-desc truncated">{description}</p>
          </div>
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

  if (hasUsageStat) {
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

  if (hasColumnBadges) {
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
        component: ({ name, isActionEnabled }, index) => {
          if (!isActionEnabled) {
            return null;
          }
          return (
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
                  <MenuItem
                    onClick={() => {
                      const link = getColumnLink(tableParams, name);
                      navigator.clipboard.writeText(link);
                    }}
                  >
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
    if (openedColumnsMap[rowValues.name]) {
      return;
    }
    openedColumnsMap[rowValues.name] = true;
    logAction({
      command: 'click',
      label: `${rowValues.content.title} ${rowValues.type.type}`,
      target_id: `column::${rowValues.content.title}`,
      target_type: 'column stats',
    });
    const tableKey = buildTableKey(rowValues.tableParams);
    getColumnLineageDispatch(tableKey, rowValues.name);
  };

  return (
    <Table
      columns={formattedColumns}
      data={flattenedData}
      options={{
        rowHeight: 72,
        emptyMessage: EMPTY_MESSAGE,
        expandRow: ExpandedRowComponent,
        onExpand: handleRowExpand,
        tableClassName: 'table-detail-table',
        preExpandRow: selectedIndex,
      }}
    />
  );
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    { getColumnLineageDispatch: getTableColumnLineage },
    dispatch
  );

export default connect<{}, DispatchFromProps, ComponentProps>(
  null,
  mapDispatchToProps
)(ColumnList);
