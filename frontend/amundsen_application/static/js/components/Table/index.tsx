// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { FormattedDataType } from 'interfaces/ColumnList';
import { IconSizes } from 'interfaces/Enums';

import ShimmeringResourceLoader from '../ShimmeringResourceLoader';
import { RightTriangleIcon, DownTriangleIcon } from '../SVGIcons';

import {
  ARRAY_KIND,
  ARRAY_LABEL,
  ARRAY_OPENER,
  ARRAY_CLOSER,
  COLUMN_NAME_REGEX,
  MAP_KIND,
  MAP_LABEL,
  MAP_OPENER,
  MAP_CLOSER,
  TYPE_METADATA_REGEX,
  MAP_KEY_NAME,
  MAP_VALUE_NAME,
  MAP_KEY_DISPLAY_NAME,
  MAP_VALUE_DISPLAY_NAME,
} from './constants';
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
  /** Callback when a row is clicked */
  onRowClick?: (rowValues: any, index: string) => void;
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
  /** Expand all child rows by default if the total number of rows does not exceed this value */
  maxNumRows?: number;
  /** Specifies if all the child rows should be expanded if true */
  shouldExpandAllRows?: boolean;
  /** Toggles to expand or collapse all rows */
  toggleExpandingRows?: () => void;
  /** Specifies whether one or more rows are expandable */
  hasRowsToExpand?: () => boolean;
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
  onRowClick?: (rowValues: any, key: string) => void;
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
  onRowClick?: (rowValues: any, key: string) => void;
  expandRowRef?: React.RefObject<HTMLTableRowElement>;
  expandedRows: RowKey[];
  setExpandedRows: (keys: string[]) => void;
  formatChildrenData?: (item: any, index: number) => FormattedDataType;
  preExpandRightPanel?: (columnDetails: FormattedDataType) => void;
  nestedLevel: number;
};

type ExpandCollapseAllRowsInput = {
  allColumnKeys: string[];
  shouldExpandAllRows: boolean | undefined;
  setExpandedRows: (keys: string[]) => void;
  initialExpandedRows: string[];
  maxNumRows: number | undefined;
  toggleExpandingRows: (() => void) | undefined;
};

type TableHooksInput = {
  data: ValidData[];
  maxNumRows: number | undefined;
  preExpandPanelKey: string | undefined;
  tableKey: string | undefined;
  shouldExpandAllRows: boolean | undefined;
  toggleExpandingRows: (() => void) | undefined;
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

const updateMapDisplayNames = (childrenData) =>
  childrenData.map((child) => {
    let displayName = child.name;

    if (child.name === MAP_KEY_NAME) {
      displayName = MAP_KEY_DISPLAY_NAME;
    } else if (child.name === MAP_VALUE_NAME) {
      displayName = MAP_VALUE_DISPLAY_NAME;
    }

    return { ...child, content: { ...child.content, title: displayName } };
  });

const getAllColumnKeys = (columns) =>
  columns.reduce((prevKeys, col: FormattedDataType) => {
    let childKeys = [];

    if (col.typeMetadata?.children?.length) {
      childKeys = getAllColumnKeys(col.typeMetadata.children);
    } else if (col.children?.length) {
      childKeys = getAllColumnKeys(col.children);
    }

    return [...prevKeys, col.key, ...childKeys];
  }, []);

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

const getInitialExpandedRows = (
  data,
  allColumnKeys,
  maxNumRows,
  preExpandPanelKey,
  tableKey
) =>
  allColumnKeys.length <= maxNumRows
    ? allColumnKeys
    : getKeysToExpand(preExpandPanelKey, tableKey);

const expandOrCollapseAllRows = ({
  allColumnKeys,
  shouldExpandAllRows,
  setExpandedRows,
  initialExpandedRows,
  maxNumRows,
  toggleExpandingRows,
}: ExpandCollapseAllRowsInput) => {
  if (shouldExpandAllRows !== undefined) {
    if (shouldExpandAllRows) {
      setExpandedRows(allColumnKeys);
    } else {
      setExpandedRows([]);
    }
  } else if (maxNumRows && allColumnKeys.length > maxNumRows) {
    // This case is hit when first loading the page and all rows should be collapsed by default
    if (initialExpandedRows.length > 0) {
      // A subset of initial rows to expand has been specified
      setExpandedRows(initialExpandedRows);
    } else if (toggleExpandingRows) {
      // Sets the value to false so the page knows to display the option to expand all rows
      // instead of the default of collapse all
      toggleExpandingRows();
    }
  }
};

const getFormattedChildrenData = (item, formatChildrenData) =>
  item.typeMetadata
    ? [item.typeMetadata].map(formatChildrenData)
    : item.children.map(formatChildrenData);

const handleSpecificTypeRowData = (initialRowValues, formatChildrenData) => {
  // Retrieve the initial formatted child data and row values to be displayed
  let formattedChildren = initialRowValues.typeMetadata
    ? getFormattedChildrenData(initialRowValues, formatChildrenData)
    : [];
  let rowValuesToDisplay = initialRowValues.typeMetadata
    ? formattedChildren[0]
    : initialRowValues;

  // Handle array kinds
  let arrayCount = 0;
  while (rowValuesToDisplay.kind === ARRAY_KIND) {
    // Keep track of how many nested array levels there are
    arrayCount++;
    formattedChildren = getFormattedChildrenData(
      rowValuesToDisplay,
      formatChildrenData
    );

    // Skip over any array type metadata by moving on to the next child level
    if (formattedChildren[0].isExpandable) {
      [rowValuesToDisplay] = formattedChildren;
    } else {
      if (formattedChildren[0].kind === ARRAY_KIND) {
        arrayCount++;
      }
      break;
    }
  }

  if (rowValuesToDisplay.kind === ARRAY_KIND) {
    // The innermost nested kind is array, so don't display an extra row for its terminal state
    formattedChildren = [];
  } else {
    // Get the formatted children for the final rowValuesToDisplay
    formattedChildren = getFormattedChildrenData(
      rowValuesToDisplay,
      formatChildrenData
    );

    if (rowValuesToDisplay.kind === MAP_KIND) {
      formattedChildren = updateMapDisplayNames(formattedChildren);
    }
  }

  return { rowValuesToDisplay, formattedChildren, arrayCount };
};

const getSpecificTypeOpenerRow = (
  rowValuesToDisplay,
  arrayCount,
  nestedLevel,
  additionalTableColCount
) => {
  const hasSpecificTypeHandling =
    arrayCount > 0 || rowValuesToDisplay.kind === MAP_KIND;
  if (!hasSpecificTypeHandling) {
    return null;
  }

  let arrayOpenerLabel = '';
  if (arrayCount > 0) {
    arrayOpenerLabel = ARRAY_LABEL + ARRAY_OPENER.repeat(arrayCount);
  }

  let mapOpenerLabel = '';
  if (rowValuesToDisplay.kind === MAP_KIND) {
    mapOpenerLabel = MAP_LABEL + MAP_OPENER;
  }

  const cellStyle = {
    paddingLeft: getIndentationPaddingSize(nestedLevel, false),
  };

  return (
    <tr
      className="ams-table-row is-nested-column-row is-specific-type-row"
      key={`openerRow:${rowValuesToDisplay.key}`}
    >
      <td key={`openerCell:${rowValuesToDisplay.key}`} style={cellStyle}>
        <span className="column-type-label">
          {arrayOpenerLabel} {mapOpenerLabel}
        </span>
      </td>
      {[...Array(additionalTableColCount)].map((value, index) => (
        <td key={`openerCellPlaceholder${index}:${rowValuesToDisplay.key}`} />
      ))}
    </tr>
  );
};

const getSpecificTypeCloserRow = (
  rowValuesToDisplay,
  arrayCount,
  nestedLevel,
  additionalTableColCount
) => {
  const hasSpecificTypeHandling =
    arrayCount > 0 || rowValuesToDisplay.kind === MAP_KIND;
  if (!hasSpecificTypeHandling) {
    return null;
  }

  let arrayCloserLabel = '';
  if (arrayCount > 0) {
    arrayCloserLabel = ARRAY_CLOSER.repeat(arrayCount);
  }

  let mapCloserLabel = '';
  if (rowValuesToDisplay.kind === MAP_KIND) {
    mapCloserLabel = MAP_CLOSER;
  }

  const cellStyle = {
    paddingLeft: getIndentationPaddingSize(nestedLevel, false),
  };

  return (
    <tr
      className="ams-table-row is-nested-column-row is-specific-type-row"
      key={`closerRow:${rowValuesToDisplay.key}`}
    >
      <td key={`closerCell:${rowValuesToDisplay.key}`} style={cellStyle}>
        <span className="column-type-label">
          {mapCloserLabel} {arrayCloserLabel}
        </span>
      </td>
      {[...Array(additionalTableColCount)].map((value, index) => (
        <td key={`closerCellPlaceholder${index}:${rowValuesToDisplay.key}`} />
      ))}
    </tr>
  );
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

type ExpandCollapseAllButtonProps = {
  shouldExpandAllRows?: boolean;
  hasRowsToExpand?: () => boolean;
  toggleExpandingRows?: () => void;
};
const ExpandCollapseAllButton: React.FC<ExpandCollapseAllButtonProps> = ({
  shouldExpandAllRows,
  hasRowsToExpand,
  toggleExpandingRows,
}: ExpandCollapseAllButtonProps) => {
  const buttonContainerStyle = {
    width: `${getExpandingButtonWidth(0)}px`,
  };

  return (
    <span
      className="ams-table-expanding-button-container"
      style={buttonContainerStyle}
    >
      {hasRowsToExpand && hasRowsToExpand() && (
        <button
          type="button"
          className="btn ams-table-expanding-button is-expand-collapse-all"
          onClick={toggleExpandingRows}
        >
          <span className="sr-only">{EXPAND_ROW_TEXT}</span>
          {shouldExpandAllRows || shouldExpandAllRows === undefined ? (
            <DownTriangleIcon size={IconSizes.SMALL} />
          ) : (
            <RightTriangleIcon size={IconSizes.SMALL} />
          )}
        </button>
      )}
    </span>
  );
};

type ExpandingButtonProps = {
  rowKey: string;
  expandedRows: RowKey[];
  rowValues: any;
  onClick: (index) => void;
  onExpand?: (rowValues: any, key: string) => void;
  onCollapse?: (rowValues: any, key: string) => void;
  nestedLevel: number;
};
const ExpandingButton: React.FC<ExpandingButtonProps> = ({
  rowKey,
  onClick,
  onExpand,
  onCollapse,
  rowValues,
  expandedRows,
  nestedLevel,
}: ExpandingButtonProps) => {
  const isExpanded = expandedRows.includes(rowKey);
  const buttonContainerStyle = {
    width: `${getExpandingButtonWidth(nestedLevel)}px`,
  };

  const handleExpandButton = (event) => {
    event.stopPropagation();

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
  };

  return (
    <span
      className="ams-table-expanding-button-container"
      style={buttonContainerStyle}
    >
      <button
        key={rowKey}
        type="button"
        className="btn ams-table-expanding-button"
        onClick={handleExpandButton}
      >
        <span className="sr-only">{EXPAND_ROW_TEXT}</span>
        {isExpanded ? (
          <DownTriangleIcon size={IconSizes.SMALL} />
        ) : (
          <RightTriangleIcon size={IconSizes.SMALL} />
        )}
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
  onRowClick,
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
      nestedLevel={nestedLevel}
    />
  );
  const handleRowClick = () => {
    onRowClick?.(rowValues, columnKey);
  };

  const rowClasses = `ams-table-row ${
    rowValues.isNestedColumn ? 'is-nested-column-row' : ''
  } ${currentSelectedKey === columnKey ? 'is-selected-row' : ''} ${
    onRowClick ? 'is-interactive-row' : ''
  }`;

  return (
    <React.Fragment key={columnKey}>
      <tr
        className={rowClasses}
        key={columnKey}
        style={rowStyles}
        ref={expandRowRef}
        onClick={handleRowClick}
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
    onRowClick,
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
        onRowClick={onRowClick}
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
      const {
        rowValuesToDisplay,
        formattedChildren,
        arrayCount,
      } = handleSpecificTypeRowData(item, formatChildrenData);

      const additionalTableColCount = columns.length - 1;
      const openerRow = getSpecificTypeOpenerRow(
        rowValuesToDisplay,
        arrayCount,
        nestedLevel,
        additionalTableColCount
      );
      const closerRow = getSpecificTypeCloserRow(
        rowValuesToDisplay,
        arrayCount,
        nestedLevel,
        additionalTableColCount
      );

      return [
        ...prevRows,
        parentRow,
        openerRow,
        ...getTableRows({
          ...tableRowDetails,
          data: formattedChildren,
          nestedLevel: nestedLevel + 1,
        }),
        closerRow,
      ];
    }

    return [...prevRows, parentRow];
  }, []);
};

const useTableHooks = ({
  data,
  maxNumRows,
  preExpandPanelKey,
  tableKey,
  shouldExpandAllRows,
  toggleExpandingRows,
}: TableHooksInput) => {
  const allColumnKeys = React.useMemo(() => getAllColumnKeys(data), [data]);
  const initialExpandedRows = React.useMemo(
    () =>
      getInitialExpandedRows(
        data,
        allColumnKeys,
        maxNumRows,
        preExpandPanelKey,
        tableKey
      ),
    [preExpandPanelKey]
  );

  const [expandedRows, setExpandedRows] = React.useState<RowKey[]>(
    initialExpandedRows
  );

  React.useEffect(() => {
    expandOrCollapseAllRows({
      allColumnKeys,
      shouldExpandAllRows,
      setExpandedRows,
      initialExpandedRows,
      maxNumRows,
      toggleExpandingRows,
    });
  }, [shouldExpandAllRows]);

  const expandRowRef = React.useRef<HTMLTableRowElement>(null);
  React.useEffect(() => {
    if (expandRowRef.current !== null) {
      expandRowRef.current.scrollIntoView();
    }
  }, []);

  return { expandedRows, setExpandedRows, expandRowRef };
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
    onRowClick,
    preExpandPanelKey,
    currentSelectedKey,
    tableKey,
    formatChildrenData,
    preExpandRightPanel,
    maxNumRows,
    shouldExpandAllRows,
    toggleExpandingRows,
    hasRowsToExpand,
  } = options;
  const fields = columns.map(({ field }) => field);
  const rowStyles = { height: `${rowHeight}px` };

  const { expandedRows, setExpandedRows, expandRowRef } = useTableHooks({
    data,
    maxNumRows,
    preExpandPanelKey,
    tableKey,
    shouldExpandAllRows,
    toggleExpandingRows,
  });

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
      onRowClick,
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
              <span
                className={`${
                  index === 0 ? 'ams-table-first-cell-contents' : ''
                }`}
              >
                {index === 0 && (
                  <ExpandCollapseAllButton
                    shouldExpandAllRows={shouldExpandAllRows}
                    hasRowsToExpand={hasRowsToExpand}
                    toggleExpandingRows={toggleExpandingRows}
                  />
                )}
                {title}
              </span>
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
