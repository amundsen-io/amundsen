// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import ShimmeringResourceLoader from '../ShimmeringResourceLoader';

import './styles.scss';

type TextAlignmentValues = 'left' | 'right' | 'center';

export interface TableColumn {
  title: string;
  field: string;
  horAlign?: TextAlignmentValues;
  // className?: string;
  // width?: number;
  // sortable?: bool (false)
  // data?: () => React.ReactNode ((row,index) => <div>{index}</div>)
  // actions?: Action[]
}

export interface TableOptions {
  tableClassName?: string;
  isLoading?: boolean;
  numLoadingBlocks?: number;
  rowHeight?: number;
}

export interface TableProps {
  columns: TableColumn[];
  data: [];
  options?: TableOptions;
}

const DEFAULT_EMPTY_MESSAGE = 'No Results';
const DEFAULT_LOADING_ITEMS = 3;
const DEFAULT_ROW_HEIGHT = 30;
const DEFAULT_TEXT_ALIGNMENT = 'left';

type RowStyles = {
  height: string;
};

type EmptyRowProps = {
  colspan: number;
  rowStyles: RowStyles;
};

const EmptyRow: React.FC<EmptyRowProps> = ({
  colspan,
  rowStyles,
}: EmptyRowProps) => (
  <tr className="ams-table-row" style={rowStyles}>
    <td className="ams-empty-message-cell" colSpan={colspan}>
      {DEFAULT_EMPTY_MESSAGE}
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
  } = options;
  const fields = columns.map(({ field }) => field);
  const rowStyles = { height: `${rowHeight}px` };

  let body: React.ReactNode = (
    <EmptyRow colspan={fields.length} rowStyles={rowStyles} />
  );

  if (data.length) {
    body = data.map((item, index) => {
      return (
        <tr className="ams-table-row" key={`index:${index}`} style={rowStyles}>
          {Object.entries(item)
            .filter(([key]) => fields.includes(key))
            .map(([key, value], index) => {
              const columnInfo = columns.find(({ field }) => field === key);
              const horAlign = columnInfo
                ? columnInfo.horAlign || DEFAULT_TEXT_ALIGNMENT
                : DEFAULT_TEXT_ALIGNMENT;
              const cellStyle = {
                textAlign: `${horAlign}` as TextAlignmentValues,
              };

              return (
                <td
                  className="ams-table-cell"
                  key={`index:${index}`}
                  style={cellStyle}
                >
                  {value}
                </td>
              );
            })}
        </tr>
      );
    });
  }

  let header: React.ReactNode = (
    <tr>
      {columns.map(({ title, horAlign = DEFAULT_TEXT_ALIGNMENT }, index) => {
        const cellStyle = {
          textAlign: `${horAlign}` as TextAlignmentValues,
        };

        return (
          <th
            className="ams-table-heading-cell"
            key={`index:${index}`}
            style={cellStyle}
          >
            {title}
          </th>
        );
      })}
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
