// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import ShimmeringResourceLoader from '../ShimmeringResourceLoader';

import './styles.scss';

export interface TableColumn {
  title: string;
  field: string;
  // className?: string;
  // horAlign?: 'left' | 'right' | 'center';
  // width?: number;
  // sortable?: bool (false)
  // data?: () => React.ReactNode ((row,index) => <div>{index}</div>)
  // actions?: Action[]
}

export interface TableOptions {
  tableClassName?: string;
  isLoading?: boolean;
  numLoadingBlocks?: number;
}

export interface TableProps {
  columns: TableColumn[];
  data: [];
  options?: TableOptions;
}

const DEFAULT_EMPTY_MESSAGE = 'No Results';
const DEFAULT_LOADING_ITEMS = 3;

type EmptyRowProps = {
  colspan: number;
};

const EmptyRow: React.FC<EmptyRowProps> = ({ colspan }: EmptyRowProps) => (
  <tr className="ams-table-row">
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
  } = options;
  const fields = columns.map(({ field }) => field);

  let body: React.ReactNode = <EmptyRow colspan={fields.length} />;

  if (data.length) {
    body = data.map((item, index) => {
      return (
        <tr className="ams-table-row" key={`index:${index}`}>
          {Object.entries(item)
            .filter(([key]) => fields.includes(key))
            .map(([, value], index) => (
              <td className="ams-table-cell" key={`index:${index}`}>
                {value}
              </td>
            ))}
        </tr>
      );
    });
  }

  let header: React.ReactNode = (
    <tr>
      {columns.map(({ title }, index) => {
        return (
          <th className="ams-table-heading-cell" key={`index:${index}`}>
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
