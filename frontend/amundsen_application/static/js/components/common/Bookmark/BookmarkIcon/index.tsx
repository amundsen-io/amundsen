import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { addBookmark, removeBookmark } from "ducks/bookmark/reducer";
import { AddBookmarkRequest, RemoveBookmarkRequest } from "ducks/bookmark/types";
import { GlobalState } from "ducks/rootReducer";

import './styles.scss'


interface StateFromProps {
  isBookmarked: boolean;
}

interface DispatchFromProps {
  addBookmark: (key: string, type: string) => AddBookmarkRequest,
  removeBookmark: (key: string, type: string) => RemoveBookmarkRequest,
}

interface OwnProps {
  bookmarkKey: string;
  large?: boolean;
}

export type BookmarkIconProps = StateFromProps & DispatchFromProps & OwnProps;

export class BookmarkIcon extends React.Component<BookmarkIconProps> {
  public static defaultProps: Partial<OwnProps> = {
    large: false,
  };

  constructor(props) {
    super(props);
  }

  handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    event.preventDefault();

    if (this.props.isBookmarked) {
      this.props.removeBookmark(this.props.bookmarkKey, 'table');
    } else {
      this.props.addBookmark(this.props.bookmarkKey, 'table');
    }
  };

  render() {
    return (
      <div className={"bookmark-icon " + (this.props.large ? "bookmark-large" : "")} onClick={ this.handleClick }>
        <img className={"icon " + (this.props.isBookmarked ? "icon-bookmark-filled" : "icon-bookmark")}/>
      </div>
    )
  }
}


export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  return {
    bookmarkKey: ownProps.bookmarkKey,
    isBookmarked: state.bookmarks.myBookmarks.some((bookmark) => bookmark.key === ownProps.bookmarkKey),
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ addBookmark, removeBookmark } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, OwnProps>(mapStateToProps, mapDispatchToProps)(BookmarkIcon);
