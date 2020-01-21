import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import './styles.scss';
import { loadPreviousSearch } from 'ducks/search/reducer';
import { LoadPreviousSearchRequest } from 'ducks/search/types';

export interface OwnProps {
  path?: string;
  text?: string;
}

export interface MapDispatchToProps {
  loadPreviousSearch: () => LoadPreviousSearchRequest;
}

export type BreadcrumbProps = OwnProps & MapDispatchToProps;

export const Breadcrumb: React.SFC<BreadcrumbProps> = (props) => {
  const { path, text } = props;
  if (path !== undefined && text !== undefined) {
    return (
      <div className="amundsen-breadcrumb">
        <Link to={path} className='btn btn-flat-icon title-3'>
          <img className='icon icon-left'/>
          <span>{text}</span>
        </Link>
      </div>
    );
  }
  return (
    <div className="amundsen-breadcrumb">
      <a onClick={ props.loadPreviousSearch } className='btn btn-flat-icon title-3'>
        <img className='icon icon-left'/>
      </a>
    </div>
  );
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ loadPreviousSearch }, dispatch);
};

export default connect<{}, MapDispatchToProps>(null, mapDispatchToProps)(Breadcrumb);
