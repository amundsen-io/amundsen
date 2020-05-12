import * as React from 'react';

import { getDisplayNameByResource, getSourceDisplayName } from 'config/config-utils';

import { ResourceType } from 'interfaces/Resources';

export interface TableHeaderBulletsProps {
  cluster: string;
  database: string;
}

const TableHeaderBullets: React.SFC<TableHeaderBulletsProps> = ({ cluster, database }) => {
  return (
    <ul className="header-bullets">
      <li>{ getDisplayNameByResource(ResourceType.table)}</li>
      <li>{ getSourceDisplayName(database, ResourceType.table) }</li>
      <li>{ cluster }</li>
    </ul>
  );
};

TableHeaderBullets.defaultProps = {
  cluster: '',
  database: '',
};

export default TableHeaderBullets;
