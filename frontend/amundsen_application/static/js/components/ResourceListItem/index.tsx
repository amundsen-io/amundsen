// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import {
  Resource,
  ResourceType,
  DashboardResource,
  FeatureResource,
  TableResource,
  UserResource,
  FileResource,
  DataProviderResource,
} from 'interfaces';

import { LoggingParams } from './types';
import DashboardListItem from './DashboardListItem';
import FeatureListItem from './FeatureListItem';
import TableListItem from './TableListItem';
import UserListItem from './UserListItem';
import FileListItem from './FileListItem';
import ProviderListItem from './ProviderListItem';

import './styles.scss';
import {
  getHighlightedDashboardMetadata,
  getHighlightedTableMetadata,
  getHighlightedFeatureMetadata,
  getHighlightedFileMetadata,
  getHighlightedProviderMetadata,
} from './MetadataHighlightList/utils';

export interface ListItemProps {
  logging: LoggingParams;
  item: Resource;
}

const ResourceListItem: React.FC<ListItemProps> = ({ logging, item }) => {
  switch (item.type) {
    case ResourceType.dashboard:
      return (
        <DashboardListItem
          dashboard={item as DashboardResource}
          logging={logging}
          dashboardHighlights={getHighlightedDashboardMetadata(
            item as DashboardResource
          )}
        />
      );
    case ResourceType.feature:
      return (
        <FeatureListItem
          feature={item as FeatureResource}
          logging={logging}
          featureHighlights={getHighlightedFeatureMetadata(
            item as FeatureResource
          )}
        />
      );
    case ResourceType.table:
      return (
        <TableListItem
          table={item as TableResource}
          logging={logging}
          tableHighlights={getHighlightedTableMetadata(item as TableResource)}
        />
      );
    case ResourceType.user:
      return <UserListItem user={item as UserResource} logging={logging} />;
    case ResourceType.file:
      return (
        <FileListItem
          file={item as FileResource}
          logging={logging}
          fileHighlights={getHighlightedFileMetadata(item as FileResource)}
        />
      );
    case ResourceType.data_provider:
      return (
        <ProviderListItem
          provider={item as DataProviderResource}
          logging={logging}
          providerHighlights={getHighlightedProviderMetadata(item as DataProviderResource)}
        />
      );
    default:
      return null;
  }
};
export default ResourceListItem;
