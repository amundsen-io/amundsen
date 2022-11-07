// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { getTableLineageDisableAppListLinks } from 'config/config-utils';
import { ResourceType, TableResource } from 'interfaces/Resources';
import { LineageItem } from 'interfaces/Lineage';
import TableListItem from 'components/ResourceListItem/TableListItem';
import { getHighlightedTableMetadata } from 'components/ResourceListItem/MetadataHighlightList/utils';

import { NO_LINEAGE_INFO } from '../constants';

export interface LineageListProps {
  items: LineageItem[];
  direction: string;
}

const isTableLinkDisabled = (table: LineageItem) => {
  // check if item is currently indexed in Amundsen, if it's not mark as disabled
  if (table.in_amundsen === false) {
    return true;
  }

  // use configuration to determine weather a table link is disabled or not
  const disableAppListLinks = getTableLineageDisableAppListLinks();
  let disabled = false;
  if (disableAppListLinks) {
    disabled = Object.keys(disableAppListLinks).some((key) => {
      if (key === 'badges') {
        return (
          table.badges.filter(({ badge_name }) =>
            disableAppListLinks?.badges?.some((badge) => badge_name === badge)
          ).length === 0
        );
      }
      return disableAppListLinks![key].test(table[key]) === false;
    });
  }

  return disabled;
};

export const LineageList: React.FC<LineageListProps> = ({
  items,
  direction,
}: LineageListProps) => {
  if (items.length === 0) {
    return (
      <div className="resource-list">
        <div className="empty-message body-placeholder">{NO_LINEAGE_INFO}</div>
      </div>
    );
  }

  return (
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
};

export default LineageList;
