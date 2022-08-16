// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import AppConfig from 'config/config';
import { ResourceType, TableResource } from 'interfaces/Resources';
import { LineageItem } from 'interfaces/Lineage';
import TableListItem from 'components/ResourceListItem/TableListItem';
import { getHighlightedTableMetadata } from 'components/ResourceListItem/MetadataHighlightList/utils';

export interface LineageListProps {
  items: LineageItem[];
  direction: string;
}

const isTableLinkDisabled = (table: LineageItem) => {
  const config = AppConfig.tableLineage;
  let disabled = false;
  if (config.disableAppListLinks) {
    disabled = Object.keys(config.disableAppListLinks).some(
      (key) => config.disableAppListLinks![key].test(table[key]) === false
    );
  }
  return disabled;
};

const LineageList: React.FC<LineageListProps> = ({
  items,
  direction,
}: LineageListProps) => (
  <div className="list-group">
    {items.map((table, index) => {
      const logging = {
        index,
        source: `table_lineage_list_${direction}`,
      };
      const tableResource: TableResource = {
        ...table,
        type: ResourceType.table,
        description: '',
      };
      return (
        <TableListItem
          table={tableResource}
          logging={logging}
          key={`lineage-item::${index}`}
          tableHighlights={getHighlightedTableMetadata(tableResource)}
          disabled={isTableLinkDisabled(table)}
        />
      );
    })}
  </div>
);

export default LineageList;
