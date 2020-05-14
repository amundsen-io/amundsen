import * as React from 'react';
import { connect } from 'react-redux';
import { GlobalState } from 'ducks/rootReducer';

import './styles.scss'
import { Bookmark, ResourceType, ResourceDict } from 'interfaces';
import { getDisplayNameByResource, indexDashboardsEnabled } from 'config/config-utils';
import {
  BOOKMARK_TITLE,
  BOOKMARKS_PER_PAGE,
  EMPTY_BOOKMARK_MESSAGE,
  MY_BOOKMARKS_SOURCE_NAME,
} from './constants';
import PaginatedResourceList from 'components/common/ResourceList/PaginatedResourceList';
import TabsComponent from 'components/common/TabsComponent';

interface StateFromProps {
  myBookmarks: ResourceDict<Bookmark[]>;
  isLoaded: boolean;
}

export type MyBookmarksProps = StateFromProps;

export class MyBookmarks extends React.Component<MyBookmarksProps> {
  generateTabContent = (resource: ResourceType) => {
    const bookmarks = this.props.myBookmarks[resource];
    if (!bookmarks) {
      return null;
    }
    return (
      <PaginatedResourceList
        allItems={ bookmarks }
        emptyText={ EMPTY_BOOKMARK_MESSAGE }
        itemsPerPage={ BOOKMARKS_PER_PAGE }
        source={ MY_BOOKMARKS_SOURCE_NAME }
      />
    )
  };

  generateTabKey = (resource: ResourceType) => {
    return `bookmarktab:${resource}`;
  };

  generateTabTitle = (resource: ResourceType): string  => {
    const bookmarks = this.props.myBookmarks[resource];
    if (!bookmarks) {
      return '';
    }
    return `${getDisplayNameByResource(resource)} (${bookmarks.length})`;
  };

  generateTabInfo = () => {
    const tabInfo = [];

    tabInfo.push({
      content: this.generateTabContent(ResourceType.table),
      key: this.generateTabKey(ResourceType.table),
      title: this.generateTabTitle(ResourceType.table)
    })

    if (indexDashboardsEnabled()) {
      tabInfo.push({
        content: this.generateTabContent(ResourceType.dashboard),
        key: this.generateTabKey(ResourceType.dashboard),
        title: this.generateTabTitle(ResourceType.dashboard)
      })
    }

    return tabInfo;
  };

  render() {
    if (!this.props.isLoaded) {
      return null;
    }

    return (
      <div className="bookmark-list">
        <div className="title-1">{ BOOKMARK_TITLE }</div>
        <TabsComponent tabs={ this.generateTabInfo() } defaultTab={ this.generateTabKey(ResourceType.table) } />
      </div>
    );
  }
}


export const mapStateToProps = (state: GlobalState) => {
  return {
    myBookmarks: state.bookmarks.myBookmarks,
    isLoaded: state.bookmarks.myBookmarksIsLoaded,
  };
};

export default connect<StateFromProps>(mapStateToProps)(MyBookmarks);
