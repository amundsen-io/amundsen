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
} from 'interfaces';

import { LoggingParams } from './types';
import DashboardListItem from './DashboardListItem';
import FeatureListItem from './FeatureListItem';
import TableListItem from './TableListItem';
import UserListItem from './UserListItem';

import './styles.scss';

export interface ListItemProps {
  logging: LoggingParams;
  item: Resource;
  onItemClick: () => void;
}

export default class ResourceListItem extends React.Component<ListItemProps> {
  render() {
    const {item, logging, onItemClick} = this.props;
    switch (item.type) {
      case ResourceType.dashboard:
        return (
          <DashboardListItem
            dashboard={item as DashboardResource}
            logging={logging}
          />
        );
      case ResourceType.feature:
        return (
          <FeatureListItem
            feature={item as FeatureResource}
            logging={logging}
            onItemClick={onItemClick}
          />
        );
      case ResourceType.table:
        return (
          <TableListItem
            table={item as TableResource}
            logging={logging}
          />
        );
      case ResourceType.user:
        return (
          <UserListItem
            user={item as UserResource}
            logging={logging}
          />
        );
      default:
        return null;
    }
  }
}
