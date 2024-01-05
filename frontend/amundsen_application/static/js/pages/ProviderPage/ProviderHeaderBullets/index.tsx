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

export type ProviderHeaderBulletsProps = HeaderBulletsProps & DispatchFromProps;

export class ProviderHeaderBullets extends React.Component<ProviderHeaderBulletsProps> {
  handleClick = (e) => {
    const { name, searchDatabase } = this.props;

    logClick(e, {
      target_type: 'provider',
      label: name,
    });
    searchDatabase(name);
  };

  render() {
    const { name } = this.props;

    return (
      <ul className="header-bullets">
        <li>{getDisplayNameByResource(ResourceType.data_provider)}</li>
        <li>
          <Link to="/search" onClick={this.handleClick}>
            {getSourceDisplayName(name || '', ResourceType.data_provider)}
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
            [ResourceType.data_provider]: { name: { value: databaseText } },
          },
          submitSearch: true,
        }),
    },
    dispatch
  );

export default connect<null, DispatchFromProps, HeaderBulletsProps>(
  null,
  mapDispatchToProps
)(ProviderHeaderBullets);
