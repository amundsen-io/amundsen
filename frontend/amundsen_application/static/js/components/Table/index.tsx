// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { FormattedDataType } from 'interfaces/ColumnList';
import {
  COLUMN_NAME_REGEX,
  TYPE_METADATA_REGEX,
} from 'components/Table/constants';

import ShimmeringResourceLoader from '../ShimmeringResourceLoader';
import { UpIcon, DownIcon } from '../SVGIcons';

import './styles.scss';

export enum TextAlignmentValues {
  left = 'left',
  right = 'right',
  center = 'center',
}
export interface TableColumn {
  title: string;
  field: string;
  horAlign?: TextAlignmentValues;
  component?: (
    value: any,
    index: number,
    columnDetails: ValidData
  ) => React.ReactNode;
  width?: number;
  // sortable?: bool (false)
}
type Some = string | number | boolean | symbol | bigint | object;
type ValidData = Record<string, Some | null>; // Removes the undefined values

interface RowData {
  [key: string]: Some | null;
}

export interface TableOptions {
  /** Optional additional class name to identify the table */
  tableClassName?: string;
  /** Whether if the table contents are being loaded, shows a skeleton/shimmer loader if true */
  isLoading?: boolean;
  /** When isLoading is true, this number specifies the count of loading blocks that we will show */
  numLoadingBlocks?: number;
  /** Height of all regular (not expanded) rows */
  rowHeight?: number;
  /** Row key that is set when user navigates to a specific column link used to pre expand the details panel */
  preExpandPanelKey?: string;
  /** Callback when a row is expanded */
  onExpand?: (rowValues: any, key: string) => void;
  /** Callback when a row is collapsed */
  onCollapse?: (rowValues: any, key: string) => void;
  /** Optional empty table message to be shown */
  emptyMessage?: string;
  /** Row key of the currently seleected row */
  currentSelectedKey?: string;
  /** Key corresponding to the dataset table currently being viewed */
  tableKey?: string;
  /** Function used to format the data displayed in the expanded child rows */
  formatChildrenData?: (item: any, index: number) => FormattedDataType;
  /** Function used to pre expand the right panel with the designated details */
  preExpandRightPanel?: (columnDetails: FormattedDataType) => void;
}

export interface TableProps {
  data: RowData[];
  columns: TableColumn[];
  options?: TableOptions;
}

export interface TableRowProps {
  columnKey: string;
  currentSelectedKey?: string;
  columns: TableColumn[];
  rowValues: ValidData;
  rowStyles: { height: string };
  onExpand?: (rowValues: any, key: string) => void;
  onCollapse?: (rowValues: any, key: string) => void;
  expandRowRef?: React.RefObject<HTMLTableRowElement>;
  expandedRows: RowKey[];
  setExpandedRows: (key) => void;
  nestedLevel: number;
}

type RowStyles = {
  height: string;
};

type EmptyRowProps = {
  colspan: number;
  rowStyles: RowStyles;
  emptyMessage?: string;
};

type TableRowDetails = {
  data: ValidData[];
  columns: TableColumn[];
  currentSelectedKey?: string;
  preExpandPanelKey?: string;
  rowStyles: { height: string };
  onExpand?: (rowValues: any, key: string) => void;
  onCollapse?: (rowValues: any, key: string) => void;
  expandRowRef?: React.RefObject<HTMLTableRowElement>;
  expandedRows: RowKey[];
  setExpandedRows: (key) => void;
  formatChildrenData?: (item: any, index: number) => FormattedDataType;
  preExpandRightPanel?: (columnDetails: FormattedDataType) => void;
  nestedLevel: number;
};

const DEFAULT_EMPTY_MESSAGE = 'No Results';
const EXPAND_ROW_TEXT = 'Expand Row';
const INVALID_DATA_ERROR_MESSAGE =
  'Invalid data! Your data does not contain the fields specified on the columns property.';
const DEFAULT_LOADING_ITEMS = 3;
const DEFAULT_ROW_HEIGHT = 30;
const EXPANDING_BUTTON_WIDTH = 60;
const NESTED_EXPANDING_BUTTON_WIDTH = 40;
const FIRST_LEVEL_INDENTATION_WIDTH = 50;
const INDENTATION_WIDTH = 25;
const DEFAULT_TEXT_ALIGNMENT = TextAlignmentValues.left;
const DEFAULT_CELL_WIDTH = 'auto';
const ALIGNEMENT_TO_CLASS_MAP = {
  left: 'is-left-aligned',
  right: 'is-right-aligned',
  center: 'is-center-aligned',
};

const getCellAlignmentClass = (alignment: TextAlignmentValues) =>
  ALIGNEMENT_TO_CLASS_MAP[alignment];

const getExpandingButtonWidth = (nestedLevel) =>
  nestedLevel === 0 ? EXPANDING_BUTTON_WIDTH : NESTED_EXPANDING_BUTTON_WIDTH;

const getIndentationPaddingSize = (nestedLevel, isExpandable) => {
  let indentationLevelPadding = 0;
  if (nestedLevel > 0) {
    indentationLevelPadding =
      FIRST_LEVEL_INDENTATION_WIDTH + INDENTATION_WIDTH * (nestedLevel - 1);
  }
  const expandingButtonPlaceholder = !isExpandable
    ? getExpandingButtonWidth(nestedLevel)
    : 0;

  return `${indentationLevelPadding + expandingButtonPlaceholder}px`;
};

const fieldIsDefined = (field, row) => row[field] !== undefined;

const checkIfValidData = (
  data: unknown[],
  fields: string[]
): data is ValidData[] => {
  let isValid = true;

  for (let i = 0; i < fields.length; i++) {
    if (!data.some(fieldIsDefined.bind(null, fields[i]))) {
      isValid = false;
      break;
    }
  }
  return isValid;
};

const getKeysToExpand = (preExpandPanelKey, tableKey) => {
  // If the key to preexpand is a nested column, need to add each key level to the expanded row list
  let keysToExpand: string[] = [];

  if (preExpandPanelKey) {
    const columnKeyRegex = tableKey + COLUMN_NAME_REGEX;
    const columnKey = preExpandPanelKey.match(columnKeyRegex);
    if (columnKey) {
      keysToExpand = [columnKey[0]];
    }

    let nextKeyRegex = columnKeyRegex + TYPE_METADATA_REGEX;
    let nextKey = preExpandPanelKey.match(nextKeyRegex);
    while (nextKey) {
      keysToExpand = [...keysToExpand, nextKey[0]];
      nextKeyRegex += COLUMN_NAME_REGEX;
      nextKey = preExpandPanelKey.match(nextKeyRegex);
    }
  }

  return keysToExpand;
};

const EmptyRow: React.FC<EmptyRowProps> = ({
  colspan,
  rowStyles,
  emptyMessage = DEFAULT_EMPTY_MESSAGE,
}: EmptyRowProps) => (
  <tr className="ams-table-row is-empty" style={rowStyles}>
    <td className="ams-empty-message-cell" colSpan={colspan}>
      {emptyMessage}
    </td>
  </tr>
);

const ShimmeringHeader: React.FC = () => (
  <tr>
    <th className="ams-table-heading-loading-cell">
      <div className="ams-table-shimmer-block" />
    </th>
  </tr>
);

type ShimmeringBodyProps = {
  numLoadingBlocks: number;
};

const ShimmeringBody: React.FC<ShimmeringBodyProps> = ({
  numLoadingBlocks,
}: ShimmeringBodyProps) => (
  <tr className="ams-table-row">
    <td className="ams-table-body-loading-cell">
      <ShimmeringResourceLoader numItems={numLoadingBlocks} />
    </td>
  </tr>
);

type ExpandingButtonProps = {
  rowKey: string;
  expandedRows: RowKey[];
  rowValues: any;
  onClick: (index) => void;
  onExpand?: (rowValues: any, key: string) => void;
  onCollapse?: (rowValues: any, key: string) => void;
  isSelectedRow: boolean;
  nestedLevel: number;
};
const ExpandingButton: React.FC<ExpandingButtonProps> = ({
  rowKey,
  onClick,
  onExpand,
  onCollapse,
  rowValues,
  expandedRows,
  isSelectedRow,
  nestedLevel,
}: ExpandingButtonProps) => {
  const isExpanded = expandedRows.includes(rowKey);
  const buttonContainerStyle = {
    width: `${getExpandingButtonWidth(nestedLevel)}px`,
  };

  return (
    <span
      className="ams-table-expanding-button-container"
      style={buttonContainerStyle}
    >
      <button
        key={rowKey}
        type="button"
        className={`btn ams-table-expanding-button ${
          rowValues.isNestedColumn ? 'is-nested-column-row' : ''
        } ${isSelectedRow ? 'is-selected-row' : ''}`}
        onClick={() => {
          const newExpandedRows = isExpanded
            ? expandedRows.filter((k) => k !== rowKey)
            : [...expandedRows, rowKey];

          onClick(newExpandedRows);

          if (!isExpanded && onExpand) {
            onExpand(rowValues, rowKey);
          }
          if (isExpanded && onCollapse) {
            onCollapse(rowValues, rowKey);
          }
        }}
      >
        <span className="sr-only">{EXPAND_ROW_TEXT}</span>
        {isExpanded ? <UpIcon /> : <DownIcon />}
      </button>
    </span>
  );
};

const TableRow: React.FC<TableRowProps> = ({
  columnKey,
  currentSelectedKey,
  columns,
  rowValues,
  rowStyles,
  onExpand,
  onCollapse,
  expandRowRef,
  expandedRows,
  setExpandedRows,
  nestedLevel,
}: TableRowProps) => {
  const fields = columns.map(({ field }) => field);
  const expandingButton = (
    <ExpandingButton
      rowKey={columnKey}
      expandedRows={expandedRows}
      onExpand={onExpand}
      onCollapse={onCollapse}
      rowValues={rowValues}
      onClick={setExpandedRows}
      isSelectedRow={currentSelectedKey === columnKey}
      nestedLevel={nestedLevel}
    />
  );

  return (
    <React.Fragment key={columnKey}>
      <tr
        className={`ams-table-row ${
          rowValues.isNestedColumn ? 'is-nested-column-row' : ''
        } ${currentSelectedKey === columnKey ? 'is-selected-row' : ''}`}
        key={columnKey}
        style={rowStyles}
        ref={expandRowRef}
      >
        <>
          {Object.entries(rowValues)
            .filter(([key]) => fields.includes(key))
            .map(([key, value], rowIndex) => {
              const columnInfo = columns.find(({ field }) => field === key);
              const horAlign: TextAlignmentValues = columnInfo
                ? columnInfo.horAlign || DEFAULT_TEXT_ALIGNMENT
                : DEFAULT_TEXT_ALIGNMENT;
              const width =
                columnInfo && columnInfo.width
                  ? `${columnInfo.width}px`
                  : DEFAULT_CELL_WIDTH;
              // TODO: Improve the typing of this
              let cellContent: React.ReactNode | typeof value = value;
              if (columnInfo && columnInfo.component) {
                cellContent = columnInfo.component(value, rowIndex, rowValues);
              }

              const isFirstCell =
                fields.findIndex((field) => field === key) === 0;
              const hasExpandingButton = isFirstCell && rowValues.isExpandable;

              let cellStyle;
              if (isFirstCell) {
                cellStyle = {
                  width,
                  paddingLeft: getIndentationPaddingSize(
                    nestedLevel,
                    rowValues.isExpandable
                  ),
                };
              } else {
                cellStyle = { width };
              }

              return (
                <td
                  className={`ams-table-cell ${getCellAlignmentClass(
                    horAlign
                  )}`}
                  key={`index:${rowIndex}`}
                  style={cellStyle}
                >
                  <span
                    className={`${
                      isFirstCell ? 'ams-table-first-cell-contents' : ''
                    }`}
                  >
                    {hasExpandingButton && expandingButton}
                    {cellContent}
                  </span>
                </td>
              );
            })}
        </>
      </tr>
    </React.Fragment>
  );
};

type RowKey = string;

const getTableRows = (tableRowDetails: TableRowDetails) => {
  const {
    data,
    columns,
    currentSelectedKey,
    preExpandPanelKey,
    rowStyles,
    onExpand,
    onCollapse,
    expandRowRef,
    expandedRows,
    setExpandedRows,
    formatChildrenData,
    preExpandRightPanel,
    nestedLevel,
  } = tableRowDetails;

  return data.reduce((prevRows, item: FormattedDataType) => {
    if (item.key && item.key === preExpandPanelKey && preExpandRightPanel) {
      preExpandRightPanel(item);
    }

    const parentRow = (
      <TableRow
        key={item.key}
        columnKey={item.key}
        currentSelectedKey={currentSelectedKey}
        columns={columns}
        rowValues={item}
        rowStyles={rowStyles}
        onExpand={onExpand}
        onCollapse={onCollapse}
        expandRowRef={
          item.key && item.key === preExpandPanelKey ? expandRowRef : undefined
        }
        expandedRows={expandedRows}
        setExpandedRows={setExpandedRows}
        nestedLevel={nestedLevel}
      />
    );

    if (
      item.isExpandable &&
      expandedRows.includes(item.key) &&
      formatChildrenData
    ) {
      return [
        ...prevRows,
        parentRow,
        ...getTableRows({
          ...tableRowDetails,
          data:
            item.typeMetadata && item.typeMetadata.children
              ? item.typeMetadata.children.map(formatChildrenData)
              : item.children.map(formatChildrenData),
          nestedLevel: nestedLevel + 1,
        }),
      ];
    }
    return [...prevRows, parentRow];
  }, []);
};

const Table: React.FC<TableProps> = ({
  data,
  columns,
  options = {},
}: TableProps) => {
  const {
    tableClassName = '',
    isLoading = false,
    numLoadingBlocks = DEFAULT_LOADING_ITEMS,
    rowHeight = DEFAULT_ROW_HEIGHT,
    emptyMessage,
    onExpand,
    onCollapse,
    preExpandPanelKey,
    currentSelectedKey,
    tableKey,
    formatChildrenData,
    preExpandRightPanel,
  } = options;
  const fields = columns.map(({ field }) => field);
  const rowStyles = { height: `${rowHeight}px` };
  const [expandedRows, setExpandedRows] = React.useState<RowKey[]>(
    getKeysToExpand(preExpandPanelKey, tableKey)
  );
  const expandRowRef = React.useRef<HTMLTableRowElement>(null);
  React.useEffect(() => {
    if (expandRowRef.current !== null) {
      expandRowRef.current.scrollIntoView();
    }
  }, []);

  let body: React.ReactNode = (
    <EmptyRow
      colspan={fields.length}
      rowStyles={rowStyles}
      emptyMessage={emptyMessage}
    />
  );

  if (data.length) {
    if (!checkIfValidData(data, fields)) {
      throw new Error(INVALID_DATA_ERROR_MESSAGE);
    }

    body = getTableRows({
      data,
      columns,
      currentSelectedKey,
      preExpandPanelKey,
      rowStyles,
      onExpand,
      onCollapse,
      expandRowRef,
      expandedRows,
      setExpandedRows,
      formatChildrenData,
      preExpandRightPanel,
      nestedLevel: 0,
    });
  }

  let header: React.ReactNode = (
    <tr>
      {columns.map(
        ({ title, horAlign = DEFAULT_TEXT_ALIGNMENT, width = null }, index) => {
          const cellStyle = {
            width: width ? `${width}px` : DEFAULT_CELL_WIDTH,
          };

          return (
            <th
              className={`ams-table-heading-cell ${getCellAlignmentClass(
                horAlign
              )}`}
              key={`index:${index}`}
              style={cellStyle}
            >
              {title}
            </th>
          );
        }
      )}
    </tr>
  );

  if (isLoading) {
    header = <ShimmeringHeader />;
    body = <ShimmeringBody numLoadingBlocks={numLoadingBlocks} />;
  }

  return (
    <table className={`ams-table ${tableClassName || ''}`}>
      <thead className="ams-table-header">{header}</thead>
      <tbody className="ams-table-body">{body}</tbody>
    </table>
  );
};

export default Table;
