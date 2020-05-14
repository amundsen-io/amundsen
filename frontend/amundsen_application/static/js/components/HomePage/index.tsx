import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

// TODO: Use css-modules instead of 'import'
import './styles.scss';
import { SEARCH_BREADCRUMB_TEXT } from './constants';

import MyBookmarks from 'components/common/Bookmark/MyBookmarks';
import Breadcrumb from 'components/common/Breadcrumb';
import PopularTables from 'components/common/PopularTables';
import { resetSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateReset } from 'ducks/search/types';
import SearchBar from 'components/common/SearchBar';
import TagsList from 'components/common/TagsList';


export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

export class HomePage extends React.Component<HomePageProps> {
  componentDidMount() {
    this.props.searchReset();
  }

  render() {
    return (
      <div className="container home-page">
        <div className="row">
          <div className="col-xs-12 col-md-offset-1 col-md-10">
            <SearchBar />
            <div className="filter-breadcrumb pull-right">
              <Breadcrumb
                direction="right"
                path="/search"
                text={SEARCH_BREADCRUMB_TEXT}
              />
            </div>
            <div className="home-element-container">
              <div id="browse-tags-header" className="title-1 browse-tags-header">Browse Tags</div>
              <TagsList />
            </div>
            <div className="home-element-container">
              <MyBookmarks />
            </div>
            <div className="home-element-container">
              <PopularTables />
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({
    searchReset: () => resetSearchState(),
  }, dispatch);
};

export default connect<DispatchFromProps>(null, mapDispatchToProps)(HomePage);
