import * as React from 'react';
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux';
import { ResourceType, Tag } from 'interfaces';

import { setSearchInputByResource, SetSearchInputRequest } from 'ducks/search/filters/reducer';
import { logClick } from 'ducks/utilMethods';

import './styles.scss';

interface OwnProps {
  data: Tag;
  compact?: boolean;
}

export interface DispatchFromProps {
  searchTag: (tagName: string) => SetSearchInputRequest;
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
    /* Note: Pattern intentionally isolates component from extraneous hardcoded parameters */
    /* Note: This will have to be extended to all resources that support tags */
    searchTag: (tagName: string) => setSearchInputByResource({ 'tag': tagName }, ResourceType.table, 0, '')
  }, dispatch);
};

export default connect<null, DispatchFromProps, OwnProps>(null, mapDispatchToProps)(TagInfo);
