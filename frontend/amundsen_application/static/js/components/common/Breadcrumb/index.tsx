import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import './styles.scss';
import { GlobalState } from 'ducks/rootReducer';
import { loadPreviousSearch } from 'ducks/search/reducer';
import { LoadPreviousSearchRequest } from 'ducks/search/types';

export interface OwnProps {
  path?: string;
  text?: string;
}

export interface StateFromProps {
  searchTerm: string;
}

export interface MapDispatchToProps {
  loadPreviousSearch: () => LoadPreviousSearchRequest;
}

export type BreadcrumbProps = OwnProps & StateFromProps & MapDispatchToProps;

export const Breadcrumb: React.SFC<BreadcrumbProps> = (props) => {
  let path = props.path;
  let text = props.text;
  if (!path && !text) {
    path = '/';
    text = 'Home';
    if (props.searchTerm) {
      return (
        <div className="amundsen-breadcrumb">
          <a onClick={ props.loadPreviousSearch } className='btn btn-flat-icon title-3'>
            <img className='icon icon-left'/>
            <span>Search Results</span>
          </a>
        </div>
      );
    }
  }
  return (
    <div className="amundsen-breadcrumb">
      <Link to={path} className='btn btn-flat-icon title-3'>
        <img className='icon icon-left'/>
        <span>{text}</span>
      </Link>
    </div>
  );
};

export const mapStateToProps = (state: GlobalState) => {
  return {
    searchTerm: state.search.search_term,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ loadPreviousSearch }, dispatch);
};

export default connect<StateFromProps, MapDispatchToProps>(mapStateToProps, mapDispatchToProps)(Breadcrumb);
