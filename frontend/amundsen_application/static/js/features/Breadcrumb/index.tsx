// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import { loadPreviousSearch } from 'ducks/search/reducer';
import { LoadPreviousSearchRequest } from 'ducks/search/types';
import { logClick } from 'utils/analytics';

import './styles.scss';

export interface OwnProps {
  direction?: BreadcrumbDirection;
  path?: string;
  text?: string;
}

export interface MapDispatchToProps {
  loadPreviousSearch: () => LoadPreviousSearchRequest;
}

type BreadcrumbDirection = 'left' | 'right';

export type BreadcrumbProps = OwnProps & MapDispatchToProps;

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  direction = 'left',
  path,
  text,
  loadPreviousSearch,
}) => {
  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    logClick(e, {
      label: 'Advanced Search',
    });
  };

  const handlePreviousSearchClick = (
    e: React.MouseEvent<HTMLAnchorElement>
  ) => {
    logClick(e, {
      label: 'Back to search',
    });
    loadPreviousSearch();
  };

  if (path !== undefined && text !== undefined) {
    return (
      <div className="amundsen-breadcrumb">
        <Link
          to={path}
          className="btn btn-flat-icon text-title-w3"
          onClick={handleClick}
          data-type="advanced-search"
        >
          {direction === 'left' && <img className="icon icon-left" alt="" />}
          <span>{text}</span>
          {direction === 'right' && <img className="icon icon-right" alt="" />}
        </Link>
      </div>
    );
  }

  return (
    <div className="amundsen-breadcrumb">
      {/* eslint-disable jsx-a11y/anchor-is-valid */}
      <a
        onClick={handlePreviousSearchClick}
        className="btn btn-flat-icon text-title-w3"
        data-type="back-to-search"
      >
        {direction === 'left' && <img className="icon icon-left" alt="" />}
        {direction === 'right' && <img className="icon icon-right" alt="" />}
      </a>
    </div>
  );
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ loadPreviousSearch }, dispatch);

export default connect<{}, MapDispatchToProps>(
  null,
  mapDispatchToProps
)(Breadcrumb);
