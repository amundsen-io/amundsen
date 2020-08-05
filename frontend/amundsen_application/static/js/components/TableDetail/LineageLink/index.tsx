// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import AvatarLabel from 'components/common/AvatarLabel';
import AppConfig from 'config/config';
import { logClick } from 'ducks/utilMethods';
import { TableMetadata } from 'interfaces/TableMetadata';

export interface LineageLinkProps {
  tableData: TableMetadata;
}

const LineageLink: React.FC<LineageLinkProps> = ({
  tableData,
}: LineageLinkProps) => {
  const config = AppConfig.tableLineage;
  if (!config.isEnabled) return null;

  const { database, cluster, schema, name } = tableData;
  const href = config.urlGenerator(database, cluster, schema, name);
  if (!href) return null;

  const label = 'Lineage';

  return (
    <a
      className="header-link"
      href={href}
      target="_blank"
      id="explore-lineage"
      onClick={logClick}
      rel="noreferrer"
    >
      <AvatarLabel label={label} src={config.iconPath} />
    </a>
  );
};

export default LineageLink;
