// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import AvatarLabel from 'components/AvatarLabel';
import { TableMetadata } from 'interfaces/TableMetadata';
import { getTableLineageConfiguration } from 'config/config-utils';
import { logClick } from 'utils/analytics';

export interface LineageLinkProps {
  tableData: TableMetadata;
}

export const LineageLink: React.FC<LineageLinkProps> = ({
  tableData,
}: LineageLinkProps) => {
  const { urlGenerator, externalEnabled, iconPath } =
    getTableLineageConfiguration();

  if (!externalEnabled) {
    return null;
  }

  const { database, cluster, schema, name } = tableData;
  const href = urlGenerator(database, cluster, schema, name);

  if (!href) {
    return null;
  }

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
      <AvatarLabel label={label} src={iconPath} />
    </a>
  );
};

export default LineageLink;
