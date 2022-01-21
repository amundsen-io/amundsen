// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { ResourceType, Tag } from 'interfaces';

import { updateSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { logClick } from 'utils/analytics';

import './styles.scss';

interface OwnProps {
  data: Tag;
  compact?: boolean;
}

export interface DispatchFromProps {
  searchTag: (tagName: string) => UpdateSearchStateRequest;
}

export type TagInfoProps = OwnProps & DispatchFromProps;

export class TagInfo extends React.Component<TagInfoProps> {
  static defaultProps = {
    compact: true,
  };

  onClick = (e) => {
    const { data, searchTag } = this.props;
    const name = data.tag_name;
    logClick(e, {
      target_type: 'tag',
      label: name,
    });
    searchTag(name);
  };

  render() {
    const { data, compact } = this.props;
    const name = data.tag_name;

    return (
      <button
        id={`tag::${name}`}
        className={'btn tag-button' + (compact ? ' compact' : '')}
        type="button"
        onClick={this.onClick}
      >
        <span className="tag-name">{name}</span>
        {!compact && <span className="tag-count">{data.tag_count}</span>}
      </button>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      searchTag: (tagName: string) =>
        updateSearchState({
          filters: {
            [ResourceType.dashboard]: { tag: { value: tagName } },
            [ResourceType.feature]: { tag: { value: tagName } },
            [ResourceType.table]: { tag: { value: tagName } },
          },
          submitSearch: true,
        }),
    },
    dispatch
  );

export default connect<null, DispatchFromProps, OwnProps>(
  null,
  mapDispatchToProps
)(TagInfo);
