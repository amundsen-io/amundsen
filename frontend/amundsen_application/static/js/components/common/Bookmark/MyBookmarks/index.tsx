import * as React from 'react';
import { connect } from 'react-redux';
import { GlobalState } from 'ducks/rootReducer';

import './styles.scss'
import { Bookmark } from 'interfaces';
import {
  BOOKMARK_TITLE,
  BOOKMARKS_PER_PAGE,
  EMPTY_BOOKMARK_MESSAGE,
  MY_BOOKMARKS_SOURCE_NAME,
} from './constants';
import ResourceList from 'components/common/ResourceList';

interface StateFromProps {
  myBookmarks: Bookmark[];
  isLoaded: boolean;
}

export type MyBookmarksProps = StateFromProps;

export class MyBookmarks extends React.Component<MyBookmarksProps> {
  constructor(props) {
    super(props);
  }

  render() {
    if (!this.props.isLoaded) {
      return null;
    }

    const bookmarksLength = this.props.myBookmarks.length;
    return (
      <div className="bookmark-list">
        <div className="title-1">{ BOOKMARK_TITLE }</div>
        {
          bookmarksLength === 0 &&
          <div className="empty-message body-placeholder">
            { EMPTY_BOOKMARK_MESSAGE }
          </div>
        }
        {
          bookmarksLength !== 0 &&
          <ResourceList
            allItems={ this.props.myBookmarks }
            source={ MY_BOOKMARKS_SOURCE_NAME }
            itemsPerPage={ BOOKMARKS_PER_PAGE }
          />
        }
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
