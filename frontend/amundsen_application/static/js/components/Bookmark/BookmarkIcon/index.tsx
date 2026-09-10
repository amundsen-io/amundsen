// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { addBookmark, removeBookmark } from 'ducks/bookmark/reducer';
import {
  AddBookmarkRequest,
  RemoveBookmarkRequest,
} from 'ducks/bookmark/types';
import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'utils/analytics';

import { ResourceType } from 'interfaces';

import './styles.scss';

interface StateFromProps {
  isBookmarked: boolean;
}

interface DispatchFromProps {
  addBookmark: (key: string, type: ResourceType) => AddBookmarkRequest;
  removeBookmark: (key: string, type: ResourceType) => RemoveBookmarkRequest;
}

interface OwnProps {
  bookmarkKey: string;
  large?: boolean;
  resourceType: ResourceType;
}

export type BookmarkIconProps = StateFromProps & DispatchFromProps & OwnProps;

export class BookmarkIcon extends React.Component<BookmarkIconProps> {
  public static defaultProps: Partial<OwnProps> = {
    large: false,
  };

  handleClick = (e: React.MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    e.preventDefault();
    const {
      isBookmarked,
      removeBookmark,
      bookmarkKey,
      resourceType,
      addBookmark,
    } = this.props;

    if (isBookmarked) {
      logClick(e, {
        label: 'Remove Bookmark',
        target_id: `remove-${resourceType}-bookmark-button`,
      });
      removeBookmark(bookmarkKey, resourceType);
    } else {
      logClick(e, {
        label: 'Add Bookmark',
        target_id: `add-${resourceType}-bookmark-button`,
      });
      addBookmark(bookmarkKey, resourceType);
    }
  };

  render() {
    const { large, isBookmarked } = this.props;

    return (
      <div
        className={'bookmark-icon ' + (large ? 'bookmark-large' : '')}
        onClick={this.handleClick}
      >
        <img
          className={
            'icon ' + (isBookmarked ? 'icon-bookmark-filled' : 'icon-bookmark')
          }
          alt=""
        />
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => ({
  bookmarkKey: ownProps.bookmarkKey,
  isBookmarked: state.bookmarks.myBookmarks[ownProps.resourceType].some(
    (bookmark) => bookmark.key === ownProps.bookmarkKey
  ),
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ addBookmark, removeBookmark }, dispatch);

export default connect<StateFromProps, DispatchFromProps, OwnProps>(
  mapStateToProps,
  mapDispatchToProps
)(BookmarkIcon);
