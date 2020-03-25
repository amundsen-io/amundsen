import * as React from 'react';
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux';
import { ResourceType, Tag, SearchType } from 'interfaces';

import { submitSearchResource } from 'ducks/search/reducer';
import { SubmitSearchResourceRequest } from 'ducks/search/types';
import { logClick } from 'ducks/utilMethods';

import './styles.scss';

interface OwnProps {
  data: Tag;
  compact?: boolean;
}

export interface DispatchFromProps {
  searchTag: (tagName: string) => SubmitSearchResourceRequest;
}

export type TagInfoProps = OwnProps & DispatchFromProps;


export class TagInfo extends React.Component<TagInfoProps> {
  static defaultProps = {
    compact: true
  };

  constructor(props) {
    super(props);
  }

  onClick = (e) => {
    const name = this.props.data.tag_name;
    logClick(e, {
      target_type: 'tag',
      label: name,
    });
    this.props.searchTag(name);
  };

  render() {
    const name = this.props.data.tag_name;

    return (
      <button
        id={ `tag::${name}` }
        role="button"
        className={ "btn tag-button" + (this.props.compact ? " compact" : "") }
        onClick={ this.onClick }
      >
        <span className="tag-name">{ name }</span>
        {
          !this.props.compact &&
            <span className="tag-count">{ this.props.data.tag_count }</span>
        }
      </button>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({
    searchTag: (tagName: string) => submitSearchResource({
      resourceFilters: { 'tag': tagName },
      resource: ResourceType.table,
      pageIndex: 0,
      searchTerm: '',
      searchType: SearchType.FILTER,
      updateUrl: true,
    })
  }, dispatch);
};

export default connect<null, DispatchFromProps, OwnProps>(null, mapDispatchToProps)(TagInfo);
