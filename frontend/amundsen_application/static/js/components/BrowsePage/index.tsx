import * as React from 'react';
import * as DocumentTitle from 'react-document-title';

import './styles.scss';

import AppConfig from '../../../config/config';
import LoadingSpinner from '../common/LoadingSpinner';
import TagInfo from "../Tags/TagInfo";
import { Tag } from "../Tags/types";
import { GetAllTagsRequest } from "../../ducks/tags/reducer";

export interface StateFromProps {
  allTags: Tag[];
  isLoading: boolean;
}

export interface DispatchFromProps {
  getAllTags: () => GetAllTagsRequest;
}

interface BrowsePageState {
  curatedTags: Tag[];
  otherTags: Tag[];
  isLoading: boolean;
}

type BrowsePageProps = StateFromProps & DispatchFromProps;

class BrowsePage extends React.Component<BrowsePageProps, BrowsePageState> {
  constructor(props) {
    super(props);

    this.state = {
      curatedTags: [],
      otherTags: [],
      isLoading: this.props.isLoading,
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

  render() {
    let innerContent;
    if (this.state.isLoading) {
      innerContent = <LoadingSpinner/>;
    } else {
      innerContent = (
        <div className="container">
          <div className="row">
            <div className="col-xs-12">
              <h3 className="header">Browse Tags</h3>
              <hr className="header-hr"/>
              <div className="browse-body">
                {
                  this.state.curatedTags.map((tag, index) =>
                    <TagInfo data={ tag } compact={ false } key={ index }/>)
                }
                {
                  this.state.curatedTags.length > 0 && this.state.otherTags.length > 0 &&
                    <hr />
                }
                {
                  this.state.otherTags.map((tag, index) =>
                    <TagInfo data={ tag } compact={ false } key={ index }/>)
                }
              </div>
            </div>
          </div>
        </div>
      );
    }
    return (
      <DocumentTitle title="Browse - Amundsen">
        { innerContent }
      </DocumentTitle>
    );
  }
}

export default BrowsePage;
