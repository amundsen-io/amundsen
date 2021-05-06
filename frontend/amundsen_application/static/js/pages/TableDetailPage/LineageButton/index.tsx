// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { TableMetadata } from 'interfaces';
import { isTableLineagePageEnabled } from 'config/config-utils';
import { logClick } from 'utils/analytics';
import AppConfig from 'config/config';

export interface LineageButtonProps {
  tableData: TableMetadata;
}

const LineageButton: React.FC<LineageButtonProps> = ({
  tableData,
}: LineageButtonProps) => {
  const config = AppConfig.tableLineage;
  if (!config.isEnabled || !isTableLineagePageEnabled()) return null;

  const { database, cluster, schema, name } = tableData;
  const href = `/lineage/table/${cluster}/${database}/${schema}/${name}`;
  if (!href) return null;

  const label = 'Lineage';
  return (
    <a
      className="btn btn-default btn-lg"
      href={href}
      role="button"
      id="table-lineage-button"
      onClick={logClick}
      rel="noreferrer"
    >
      {label}
    </a>
  );
};

export default LineageButton;
