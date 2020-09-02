// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import './styles.scss';

export interface TableColumn {
  title: string;
  field: string;
  horAlign?: 'left' | 'right' | 'center';
  // width?: number;
  // className?: string;
  // sortable?: bool (false)
  // data?: () => React.ReactNode ((row,index) => <div>{index}</div>)
  // actions?: Action[]
}

export interface TableProps {
  columns: TableColumn[];
  data: [];
}

const Table: React.FC<TableProps> = ({ data, columns }: TableProps) => {
  const fields = columns.map(({ field }) => field);

  return (
    <table className="ams-table">
      <thead className="ams-table-header">
        <tr>
          {columns.map(({ title }, index) => {
            return (
              <th className="ams-table-heading-cell" key={`index:${index}`}>
                {title}
              </th>
            );
          })}
        </tr>
      </thead>
      <tbody className="ams-table-body">
        {data.map((item, index) => {
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
        })}
      </tbody>
    </table>
  );
};

export default Table;
