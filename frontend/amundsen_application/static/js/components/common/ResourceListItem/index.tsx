import * as React from 'react'

import { LoggingParams, Resource, ResourceType, TableResource, UserResource } from './types';
import TableListItem from './TableListItem';
import UserListItem from './UserListItem';

import './styles.scss';


interface ListItemProps {
  logging: LoggingParams;
  item: Resource;
}

export default class ResourceListItem extends React.Component<ListItemProps, {}> {
  constructor(props) {
    super(props);
  }

  render() {
    switch(this.props.item.type) {
      case ResourceType.table:
        return (<TableListItem table={ this.props.item as TableResource } logging={ this.props.logging } />);
      case ResourceType.user:
        return (<UserListItem user={ this.props.item as UserResource } logging={ this.props.logging } />);
      // case ResourceType.dashboard:
      default:
        return (null);
    }
  }
}
