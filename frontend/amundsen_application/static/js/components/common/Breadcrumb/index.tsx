import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import './styles.scss';
import { loadPreviousSearch } from 'ducks/search/reducer';
import { LoadPreviousSearchRequest } from 'ducks/search/types';

export interface OwnProps {
  direction?: BreadcrumbDirection;
  path?: string;
  text?: string;
}

export interface MapDispatchToProps {
  loadPreviousSearch: () => LoadPreviousSearchRequest;
}

type BreadcrumbDirection = "left" | "right";

export type BreadcrumbProps = OwnProps & MapDispatchToProps;

export const Breadcrumb: React.SFC<BreadcrumbProps> = (props) => {
  const { direction = "left", path, text } = props;
  if (path !== undefined && text !== undefined) {
    return (
      <div className="amundsen-breadcrumb">
        <Link to={path} className='btn btn-flat-icon title-3'>
          {
            direction === "left" &&
            <img className='icon icon-left'/>
          }
          <span>{text}</span>
          {
            direction === "right" &&
            <img className='icon icon-right'/>
          }
        </Link>
      </div>
    );
  }
  return (
    <div className="amundsen-breadcrumb">
      <a onClick={ props.loadPreviousSearch } className='btn btn-flat-icon title-3'>
        {
          direction === "left" &&
          <img className='icon icon-left'/>
        }
        {
          direction === "right" &&
          <img className='icon icon-right'/>
        }
      </a>
    </div>
  );
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ loadPreviousSearch }, dispatch);
};

export default connect<{}, MapDispatchToProps>(null, mapDispatchToProps)(Breadcrumb);
