// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import ShimmeringResourceLoader from '../ShimmeringResourceLoader';
import { UpIcon, DownIcon } from '../SVGIcons';

import './styles.scss';

type TextAlignmentValues = 'left' | 'right' | 'center';

export interface TableColumn {
  title: string;
  field: string;
  horAlign?: TextAlignmentValues;
  component?: (value: any, index: number) => React.ReactNode;
  width?: number;
  // sortable?: bool (false)
}

export interface TableOptions {
  tableClassName?: string;
  isLoading?: boolean;
  numLoadingBlocks?: number;
  rowHeight?: number;
  expandRow?: (rowValue: any, index: number) => React.ReactNode;
  onExpand?: (rowValues: any, index: number) => void;
  onCollapse?: (rowValues: any, index: number) => void;
  emptyMessage?: string;
}

export interface TableProps {
  columns: TableColumn[];
  data: any[];
  options?: TableOptions;
}

const DEFAULT_EMPTY_MESSAGE = 'No Results';
const EXPAND_ROW_TEXT = 'Expand Row';
const DEFAULT_LOADING_ITEMS = 3;
const DEFAULT_ROW_HEIGHT = 30;
const EXPANDING_CELL_WIDTH = '70px';
const DEFAULT_TEXT_ALIGNMENT = 'left';
const DEFAULT_CELL_WIDTH = 'auto';
const ALIGNEMENT_TO_CLASS_MAP = {
  left: 'is-left-aligned',
  right: 'is-right-aligned',
  center: 'is-center-aligned',
};

type RowStyles = {
  height: string;
};

type EmptyRowProps = {
  colspan: number;
  rowStyles: RowStyles;
  emptyMessage?: string;
};

const getCellAlignmentClass = (alignment: TextAlignmentValues) =>
  ALIGNEMENT_TO_CLASS_MAP[alignment];

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

type ExpandingCellProps = {
  index: number;
  expandedRows: RowIndex[];
  rowValues: any;
  onClick: (index) => void;
  onExpand?: (rowValues: any, index: number) => void;
  onCollapse?: (rowValues: any, index: number) => void;
};
const ExpandingCell: React.FC<ExpandingCellProps> = ({
  index,
  onClick,
  onExpand,
  onCollapse,
  rowValues,
  expandedRows,
}: ExpandingCellProps) => {
  const isExpanded = expandedRows.includes(index);
  const cellStyling = { width: EXPANDING_CELL_WIDTH };

  return (
    <td
      className="ams-table-cell ams-table-expanding-cell"
      key={`expandingIndex:${index}`}
      style={cellStyling}
    >
      <button
        type="button"
        className="ams-table-expanding-button"
        onClick={() => {
          const newExpandedRows = isExpanded
            ? expandedRows.filter((i) => i !== index)
            : [...expandedRows, index];

          onClick(newExpandedRows);

          if (!isExpanded && onExpand) {
            onExpand(rowValues, index);
          }
          if (isExpanded && onCollapse) {
            onCollapse(rowValues, index);
          }
        }}
      >
        <span className="sr-only">{EXPAND_ROW_TEXT}</span>
        {isExpanded ? <UpIcon /> : <DownIcon />}
      </button>
    </td>
  );
};

type RowIndex = number;

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
    expandRow = null,
    emptyMessage,
    onExpand,
    onCollapse,
  } = options;
  const fields = columns.map(({ field }) => field);
  const rowStyles = { height: `${rowHeight}px` };
  const [expandedRows, setExpandedRows] = React.useState<RowIndex[]>([]);

  let body: React.ReactNode = (
    <EmptyRow
      colspan={fields.length}
      rowStyles={rowStyles}
      emptyMessage={emptyMessage}
    />
  );

  if (data.length) {
    body = data.map((item, index) => {
      return (
        <React.Fragment key={`index:${index}`}>
          <tr
            className={`ams-table-row ${
              expandRow && expandedRows.includes(index)
                ? 'has-child-expanded'
                : ''
            }`}
            key={`index:${index}`}
            style={rowStyles}
          >
            <>
              {expandRow ? (
                <ExpandingCell
                  index={index}
                  expandedRows={expandedRows}
                  onExpand={onExpand}
                  onCollapse={onCollapse}
                  rowValues={item}
                  onClick={setExpandedRows}
                />
              ) : null}
              {Object.entries(item)
                .filter(([key]) => fields.includes(key))
                .map(([key, value], index) => {
                  const columnInfo = columns.find(({ field }) => field === key);
                  const horAlign = columnInfo
                    ? columnInfo.horAlign || DEFAULT_TEXT_ALIGNMENT
                    : DEFAULT_TEXT_ALIGNMENT;
                  const width =
                    columnInfo && columnInfo.width
                      ? `${columnInfo.width}px`
                      : DEFAULT_CELL_WIDTH;
                  const cellStyle = {
                    width,
                  };
                  // TODO: Improve the typing of this
                  let cellContent: React.ReactNode | typeof value = value;
                  if (columnInfo && columnInfo.component) {
                    cellContent = columnInfo.component(value, index);
                  }

                  return (
                    <td
                      className={`ams-table-cell ${getCellAlignmentClass(
                        horAlign
                      )}`}
                      key={`index:${index}`}
                      style={cellStyle}
                    >
                      {cellContent}
                    </td>
                  );
                })}
            </>
          </tr>
          {expandRow ? (
            <tr
              className={`ams-table-expanded-row ${
                expandedRows.includes(index) ? 'is-expanded' : ''
              }`}
              key={`expandedIndex:${index}`}
            >
              <td className="ams-table-cell">
                {/* Placeholder for the collapse/expand cell */}
              </td>
              <td className="ams-table-cell" colSpan={fields.length + 1}>
                {expandRow(item, index)}
              </td>
            </tr>
          ) : null}
        </React.Fragment>
      );
    });
  }

  let header: React.ReactNode = (
    <tr>
      {expandRow && (
        <th key="emptyTableHeading" className="ams-table-heading-cell" />
      )}
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
