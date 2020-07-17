// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import './styles.scss';

import ShimmeringTagListLoader from 'components/common/ShimmeringTagListLoader';

import TagInfo from 'components/Tags/TagInfo';
import { Tag } from 'interfaces';

import { GlobalState } from 'ducks/rootReducer';
import { getAllTags } from 'ducks/tags/reducer';
import { GetAllTagsRequest } from 'ducks/tags/types';
import { getCuratedTags, showAllTags } from 'config/config-utils';

export interface StateFromProps {
  curatedTags: Tag[];
  otherTags: Tag[];
  isLoading: boolean;
}

export interface DispatchFromProps {
  getAllTags: () => GetAllTagsRequest;
}

export type TagsListProps = StateFromProps & DispatchFromProps;

export class TagsList extends React.Component<TagsListProps> {
  componentDidMount() {
    this.props.getAllTags();
  }

  generateTagInfo(tagArray: Tag[]) {
    return tagArray.map((tag, index) => (
      <TagInfo data={tag} compact={false} key={index} />
    ));
  }

  render() {
    const { isLoading, curatedTags, otherTags } = this.props;

    if (isLoading) {
      return <ShimmeringTagListLoader />;
    }

    return (
      <div id="tags-list" className="tags-list">
        {this.generateTagInfo(curatedTags)}
        {showAllTags() && curatedTags.length > 0 && otherTags.length > 0 && (
          <hr />
        )}
        {showAllTags() &&
          otherTags.length > 0 &&
          this.generateTagInfo(otherTags)}
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  // TODO: These functions are selectors, consider moving them into the ducks
  const curatedTagsList = getCuratedTags();
  const allTags = state.tags.allTags.tags;
  const curatedTags = allTags.filter(
    (tag) => curatedTagsList.indexOf(tag.tag_name) !== -1
  );
  const otherTags = allTags.filter(
    (tag) => curatedTagsList.indexOf(tag.tag_name) === -1
  );

  return {
    curatedTags,
    otherTags,
    isLoading: state.tags.allTags.isLoading,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getAllTags }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(TagsList);
