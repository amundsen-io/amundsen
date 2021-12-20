// Copyright Contributors to the Amundsen project.	/*
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import {
  getDisplayNameByResource,
  getSourceDisplayName,
} from 'config/config-utils';

import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { updateSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { logClick } from 'utils/analytics';

import { ResourceType } from 'interfaces/Resources';

import { TABLE_VIEW_TEXT } from './constants';

export interface HeaderBulletsProps {
  cluster: string;
  database: string;
  isView: boolean;
}
export interface DispatchFromProps {
  searchDatabase: (databaseText: string) => UpdateSearchStateRequest;
}

export type TableHeaderBulletsProps = HeaderBulletsProps & DispatchFromProps;

export class TableHeaderBullets extends React.Component<TableHeaderBulletsProps> {
  handleClick = (e) => {
    const { database, searchDatabase } = this.props;
    const databaseText = database;
    logClick(e, {
      target_type: 'database',
      label: databaseText,
    });
    searchDatabase(databaseText);
  };

  render() {
    const { isView, database, cluster } = this.props;
    const isViewCheck = isView === undefined ? false : isView;
    return (
      <ul className="header-bullets">
        <li>{getDisplayNameByResource(ResourceType.table)}</li>
        <li>
          <Link to="/search" onClick={this.handleClick}>
            {getSourceDisplayName(database || '', ResourceType.table)}
          </Link>
        </li>
        <li>{cluster || ''}</li>
        {isViewCheck && <li>{TABLE_VIEW_TEXT}</li>}
      </ul>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      searchDatabase: (databaseText: string) =>
        updateSearchState({
          filters: {
            [ResourceType.table]: { database: { value: databaseText } },
          },
          submitSearch: true,
        }),
    },
    dispatch
  );

export default connect<null, DispatchFromProps, HeaderBulletsProps>(
  null,
  mapDispatchToProps
)(TableHeaderBullets);
