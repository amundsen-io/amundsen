import * as React from 'react';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import {
  POPULAR_TABLES_LABEL,
  POPULAR_TABLES_INFO_TEXT,
  POPULAR_TABLES_SOURCE_NAME,
  POPULAR_TABLES_PER_PAGE
} from './constants';
import { TableResource } from 'interfaces';

import InfoButton from 'components/common/InfoButton';
import ResourceList from 'components/common/ResourceList';

import { getPopularTables } from 'ducks/popularTables/reducer';
import { GetPopularTablesRequest } from 'ducks/popularTables/types';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

export interface StateFromProps {
  popularTables: TableResource[];
}

export interface DispatchFromProps {
  getPopularTables: () => GetPopularTablesRequest;
}

export type PopularTablesProps = StateFromProps & DispatchFromProps;

export class PopularTables extends React.Component<PopularTablesProps> {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.getPopularTables();
  }

  render() {
    return (
      <>
        <div className="popular-tables-header">
          <label className="title-1">{POPULAR_TABLES_LABEL}</label>
          <InfoButton infoText={POPULAR_TABLES_INFO_TEXT} />
        </div>
        <ResourceList
          allItems={ this.props.popularTables }
          source={ POPULAR_TABLES_SOURCE_NAME }
          itemsPerPage={ POPULAR_TABLES_PER_PAGE }
        />
      </>
    );
  }
}
export const mapStateToProps = (state: GlobalState) => {
  return {
    popularTables: state.popularTables,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getPopularTables }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(PopularTables);
