import * as React from 'react';
import { Link } from 'react-router-dom';
import { Tag } from '../types';

import './styles.scss';

interface TagInfoProps {
  data: Tag;
  compact?: boolean;
}

class TagInfo extends React.Component<TagInfoProps, {}> {
  static defaultProps = {
    compact: true
  };

  constructor(props) {
    super(props);
  }

  render() {
    const searchUrl = `/search?searchTerm=tag:${this.props.data.tag_name}`;

    if (this.props.compact) {
      return (
        <Link role="button" to={searchUrl} className="btn tag-button compact">
          {this.props.data.tag_name}
        </Link>
      );
    }

    return (
      <Link role="button" to={searchUrl} className="btn tag-button">
        <span className="tag-name">{this.props.data.tag_name}</span>
        <span className="tag-count">{this.props.data.tag_count}</span>
      </Link>
    );
  }
}

export default TagInfo;
