import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import MyBookmarks from 'components/common/Bookmark/MyBookmarks';
import PopularTables from 'components/common/PopularTables';
import { SearchAllReset } from 'ducks/search/types';
import { searchReset } from 'ducks/search/reducer';
import SearchBar from 'components/SearchPage/SearchBar';
import TagsList from 'components/common/TagsList';


export interface DispatchFromProps {
  searchReset: () => SearchAllReset;
}

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

export class HomePage extends React.Component<HomePageProps> {
  constructor(props) {
    super(props);
  }
  
  componentDidMount() {
    this.props.searchReset();
  }

  render() {
    return (
      <div className="container home-page">
        <div className="row">
          <div className="col-xs-12 col-md-offset-1 col-md-10">
            <SearchBar />
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
  return bindActionCreators({ searchReset } , dispatch);
};

export default connect<DispatchFromProps>(null, mapDispatchToProps)(HomePage);
