// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import {
  getDisplayNameByResource,
  getSourceDisplayName,
} from 'config/config-utils';

import { ResourceType } from 'interfaces/Resources';

import { TABLE_VIEW_TEXT } from './constants';

export interface TableHeaderBulletsProps {
  cluster: string;
  database: string;
  isView: boolean;
}

const TableHeaderBullets: React.FC<TableHeaderBulletsProps> = ({
  cluster,
  database,
  isView,
}: TableHeaderBulletsProps) => {
  return (
    <ul className="header-bullets">
      <li>{getDisplayNameByResource(ResourceType.table)}</li>
      <li>{getSourceDisplayName(database, ResourceType.table)}</li>
      <li>{cluster}</li>
      {isView && <li>{TABLE_VIEW_TEXT}</li>}
    </ul>
  );
};

TableHeaderBullets.defaultProps = {
  cluster: '',
  database: '',
  isView: false,
};

export default TableHeaderBullets;
