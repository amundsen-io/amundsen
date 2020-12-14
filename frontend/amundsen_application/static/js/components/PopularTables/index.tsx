// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { TableResource } from 'interfaces';

import InfoButton from 'components/InfoButton';
import PaginatedResourceList from 'components/ResourceList/PaginatedResourceList';
import ShimmeringResourceLoader from 'components/ShimmeringResourceLoader';

import { getPopularTables } from 'ducks/popularTables/reducer';
import { GetPopularTablesRequest } from 'ducks/popularTables/types';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import {
  POPULAR_TABLES_LABEL,
  POPULAR_TABLES_INFO_TEXT,
  POPULAR_TABLES_SOURCE_NAME,
  POPULAR_TABLES_PER_PAGE,
} from './constants';

import './styles.scss';

export interface StateFromProps {
  popularTables: TableResource[];
  isLoaded: boolean;
}

export interface DispatchFromProps {
  getPopularTables: () => GetPopularTablesRequest;
}

export type PopularTablesProps = StateFromProps & DispatchFromProps;

export class PopularTables extends React.Component<PopularTablesProps> {
  componentDidMount() {
    this.props.getPopularTables();
  }

  render() {
    const { popularTables, isLoaded } = this.props;
    let content = (
      <ShimmeringResourceLoader numItems={POPULAR_TABLES_PER_PAGE} />
    );

    if (isLoaded) {
      content = (
        <PaginatedResourceList
          allItems={popularTables}
          itemsPerPage={POPULAR_TABLES_PER_PAGE}
          source={POPULAR_TABLES_SOURCE_NAME}
        />
      );
    }

    return (
      <article className="popular-table-list">
        <div className="popular-tables-header">
          <h2 className="popular-tables-header-text">{POPULAR_TABLES_LABEL}</h2>
          <InfoButton infoText={POPULAR_TABLES_INFO_TEXT} />
        </div>
        {content}
      </article>
    );
  }
}
export const mapStateToProps = (state: GlobalState) => ({
  popularTables: state.popularTables.popularTables,
  isLoaded: state.popularTables.popularTablesIsLoaded,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getPopularTables }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(PopularTables);
