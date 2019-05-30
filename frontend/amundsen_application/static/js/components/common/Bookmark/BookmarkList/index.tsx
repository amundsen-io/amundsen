import * as React from 'react';
import { connect } from 'react-redux';
import Pagination from 'react-js-pagination';
import { GlobalState } from "ducks/rootReducer";

import './styles.scss'
import { Bookmark } from "ducks/bookmark/types";
import ResourceListItem from "components/common/ResourceListItem";
import {
  ITEMS_PER_PAGE,
  EMPTY_BOOKMARK_MESSAGE,
  PAGINATION_PAGE_RANGE,
  BOOKMARK_TITLE,
} from "./constants";

interface StateFromProps {
  myBookmarks: Bookmark[];
  isLoaded: boolean;
}

export type BookmarkListProps = StateFromProps;

interface BookmarkListState {
  activePage: number;
}

export class BookmarkList extends React.Component<BookmarkListProps, BookmarkListState> {
  constructor(props) {
    super(props);

    this.state = { activePage: 0 };
  }

  onPaginationChange = (pageNumber: number) => {
    const index = pageNumber - 1;
    this.setState({ activePage: index });
  };

  render() {
    if (!this.props.isLoaded) {
      return null;
    }

    const totalBookmarks = this.props.myBookmarks.length;
    const startIndex = this.state.activePage * ITEMS_PER_PAGE;
    const displayedBookmarks = this.props.myBookmarks.slice(startIndex, startIndex + ITEMS_PER_PAGE);

    if (totalBookmarks === 0) {
      return (
        <div className="bookmark-list">
          <div className="title-1">{ BOOKMARK_TITLE }</div>
          <div className="empty-message body-placeholder">
            { EMPTY_BOOKMARK_MESSAGE }
          </div>
        </div>
      )
    }
    return (
      <div className="bookmark-list">
        <div className="title-1">{ BOOKMARK_TITLE }</div>
        <ul className="list-group">
          {
            displayedBookmarks.map((resource, index) => {
              const logging = { index: index + this.state.activePage * ITEMS_PER_PAGE , source: 'Bookmarks' };
              return <ResourceListItem item={ resource } logging={ logging } key={ index } />;
            })
          }
        </ul>
        {
          totalBookmarks > ITEMS_PER_PAGE &&
          <div className="pagination-container">
            <Pagination
              activePage={ this.state.activePage + 1 }
              itemsCountPerPage={ ITEMS_PER_PAGE }
              totalItemsCount={ totalBookmarks }
              pageRangeDisplayed={ PAGINATION_PAGE_RANGE }
              onChange={ this.onPaginationChange }
            />
          </div>
        }
      </div>
    )
  }
}


export const mapStateToProps = (state: GlobalState) => {
  return {
    myBookmarks: state.bookmarks.myBookmarks,
    isLoaded: state.bookmarks.myBookmarksIsLoaded,
  };
};

export default connect<StateFromProps>(mapStateToProps)(BookmarkList);
