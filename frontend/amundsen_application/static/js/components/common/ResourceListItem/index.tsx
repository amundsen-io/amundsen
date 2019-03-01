import * as React from 'react'

import { LoggingParams, Resource, ResourceType, TableResource } from './types';
import TableListItem from './TableListItem';

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
        return (<TableListItem item={ this.props.item as TableResource } logging={ this.props.logging } />);
      // case ListItemType.user:
      // case ListItemType.dashboard:
      default:
        return (null);
    }
  }
}
