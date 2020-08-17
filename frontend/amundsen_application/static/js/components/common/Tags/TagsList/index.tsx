// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import ShimmeringTagListLoader from 'components/common/ShimmeringTagListLoader';

import TagInfo from 'components/common/Tags/TagInfo';
import { Tag } from 'interfaces';

import {
  POPULAR_TAGS_TITLE,
  CURATED_TAGS_TITLE,
  BROWSE_MORE_TAGS_TEXT,
  OTHER_TAGS_TITLE,
  BROWSE_TAGS_TITLE,
  BROWSE_PAGE_PATH,
} from './constants';

import './styles.scss';

export type TagsListProps = StateFromProps & OwnProps;

export interface StateFromProps {
  curatedTags: Tag[];
  popularTags: Tag[];
  otherTags?: Tag[];
  isLoading?: boolean;
}

interface OwnProps {
  shortTagsList?: boolean;
}

interface TagsListTitleProps {
  titleText: string;
}

interface TagsListBlockProps {
  tags: Tag[];
}

const TagsListTitle: React.FC<TagsListTitleProps> = ({
  titleText,
}: TagsListTitleProps) => (
  <h1 className="title-1 section-title" id="browse-header">
    {titleText}
  </h1>
);

const TagsListLabel: React.FC<TagsListTitleProps> = ({
  titleText,
}: TagsListTitleProps) => (
  <label className="section-label">
    <span className="section-title title-2">{titleText}</span>
  </label>
);

const TagsListBlock: React.FC<TagsListBlockProps> = ({
  tags,
}: TagsListBlockProps) => {
  return (
    <div id="tags-list" className="tags-list">
      {tags.map((tag) => (
        <TagInfo data={tag} compact={false} key={tag.tag_name} />
      ))}
    </div>
  );
};

const ShortTagsList: React.FC<TagsListProps> = ({
  curatedTags,
  popularTags,
}: TagsListProps) => {
  const hasCuratedTags = curatedTags.length > 0;
  const hasPopularTags = popularTags.length > 0;
  return (
    <div className="short-tag-list">
      {!hasCuratedTags && hasPopularTags && (
        <TagsListTitle titleText={POPULAR_TAGS_TITLE} />
      )}
      {hasCuratedTags && <TagsListTitle titleText={CURATED_TAGS_TITLE} />}
      {!hasCuratedTags && hasPopularTags && (
        <TagsListBlock tags={popularTags} />
      )}
      {hasCuratedTags && <TagsListBlock tags={curatedTags} />}
      <Link to={BROWSE_PAGE_PATH} className="browse-tags-link">
        {BROWSE_MORE_TAGS_TEXT}
      </Link>
    </div>
  );
};

const LongTagsList: React.FC<TagsListProps> = ({
  curatedTags,
  popularTags,
  otherTags,
}: TagsListProps) => {
  const hasCuratedTags = curatedTags.length > 0;
  const hasPopularTags = popularTags.length > 0;
  const hasOtherTags = otherTags.length > 0;
  return (
    <div className="full-tag-list">
      <TagsListTitle titleText={BROWSE_TAGS_TITLE} />
      <hr className="header-hr" />
      {!hasCuratedTags && hasPopularTags && (
        <TagsListLabel titleText={POPULAR_TAGS_TITLE} />
      )}
      {hasCuratedTags && <TagsListLabel titleText={CURATED_TAGS_TITLE} />}
      {!hasCuratedTags && hasPopularTags && (
        <TagsListBlock tags={popularTags} />
      )}
      {hasCuratedTags && <TagsListBlock tags={curatedTags} />}
      {hasOtherTags && <TagsListLabel titleText={OTHER_TAGS_TITLE} />}
      {hasOtherTags && <TagsListBlock tags={otherTags} />}
    </div>
  );
};

const TagsList: React.FC<TagsListProps> = ({
  curatedTags,
  popularTags,
  otherTags,
  isLoading,
  shortTagsList,
}: TagsListProps) => {
  if (isLoading) {
    return <ShimmeringTagListLoader />;
  }

  if (shortTagsList) {
    return (
      <ShortTagsList curatedTags={curatedTags} popularTags={popularTags} />
    );
  }

  return (
    <LongTagsList
      curatedTags={curatedTags}
      popularTags={popularTags}
      otherTags={otherTags}
    />
  );
};

export default TagsList;
