import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import './styles.scss';

import AppConfig from 'config/config';
import LoadingSpinner from 'components/common/LoadingSpinner';
import TagInfo from 'components/Tags/TagInfo';
import { Tag } from 'interfaces';

import { GlobalState } from 'ducks/rootReducer';
import { getAllTags } from 'ducks/allTags/reducer';
import { GetAllTagsRequest } from 'ducks/allTags/types';

export interface StateFromProps {
  allTags: Tag[];
  isLoading: boolean;
}

export interface DispatchFromProps {
  getAllTags: () => GetAllTagsRequest;
}

interface TagsListState {
  curatedTags: Tag[];
  otherTags: Tag[];
}

export type TagsListProps = StateFromProps & DispatchFromProps;

export class TagsList extends React.Component<TagsListProps, TagsListState> {
  constructor(props) {
    super(props);

    this.state = {
      curatedTags: [],
      otherTags: [],
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const { allTags, isLoading } = nextProps;
    if (isLoading) {
      return {
        ...prevState,
        isLoading,
      };
    }

    const curatedTagsList = AppConfig.browse.curatedTags;
    const curatedTags = allTags.filter((tag) => curatedTagsList.indexOf(tag.tag_name) !== -1);

    let otherTags = [];
    if (AppConfig.browse.showAllTags) {
      otherTags = allTags.filter((tag) => curatedTagsList.indexOf(tag.tag_name) === -1);
    }
    return { curatedTags, otherTags, isLoading };
  }

  componentDidMount() {
    this.props.getAllTags();
  }

  generateTagInfo(tagArray: Tag[]) {
    return tagArray.map((tag, index) =>
      <TagInfo data={ tag } compact={ false } key={ index }/>)
  }

  render() {
    let innerContent;
    if (this.props.isLoading) {
      innerContent = <LoadingSpinner/>;
    } else {
      innerContent = (
        <div id="browse-body" className="browse-body">
          {this.generateTagInfo(this.state.curatedTags)}
          {
            this.state.curatedTags.length > 0 && this.state.otherTags.length > 0 &&
              <hr />
          }
          {this.generateTagInfo(this.state.otherTags)}
        </div>
      );
    }
    return (innerContent);
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    allTags: state.allTags.allTags,
    isLoading: state.allTags.isLoading,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getAllTags } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(TagsList);
