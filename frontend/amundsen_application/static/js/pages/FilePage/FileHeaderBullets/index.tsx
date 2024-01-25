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

export interface HeaderBulletsProps {
  name: string;
}
export interface DispatchFromProps {
  searchDatabase: (databaseText: string) => UpdateSearchStateRequest;
}

export type FileHeaderBulletsProps = HeaderBulletsProps & DispatchFromProps;

export class FileHeaderBullets extends React.Component<ProviderHeaderBulletsProps> {
  handleClick = (e) => {
    const { name, searchDatabase } = this.props;

    logClick(e, {
      target_type: 'file',
      label: name,
    });
    searchDatabase(name);
  };

  render() {
    const { name } = this.props;

    return (
      <ul className="header-bullets">
        <li>{getDisplayNameByResource(ResourceType.file)}</li>
        <li>
          <Link to="/search" onClick={this.handleClick}>
            {getSourceDisplayName(name || '', ResourceType.file)}
          </Link>
        </li>
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
            [ResourceType.file]: { name: { value: databaseText } },
          },
          submitSearch: true,
        }),
    },
    dispatch
  );

export default connect<null, DispatchFromProps, HeaderBulletsProps>(
  null,
  mapDispatchToProps
)(FileHeaderBullets);
