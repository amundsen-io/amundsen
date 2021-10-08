// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { Badge } from 'interfaces/Badges';

import { GetAllBadgesRequest } from 'ducks/badges/types';
import { getAllBadges } from 'ducks/badges/reducer';
import { connect } from 'react-redux';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import BadgeBrowseList from 'components/Badges/BadgeBrowseList';

interface OwnProps {
  shortBadgesList: boolean;
}

export interface StateFromProps {
  badges: Badge[];
  isLoading: boolean;
}

export const mapStateToProps = (state: GlobalState) => {
  const { badges } = state.badges.allBadges;

  return {
    badges,
    isLoading: state.badges.allBadges.isLoading,
  };
};

export interface DispatchFromProps {
  getAllBadges: () => GetAllBadgesRequest;
}

export type BadgesListContainerProps = StateFromProps &
  DispatchFromProps &
  OwnProps;

export class BadgesListContainer extends React.Component<BadgesListContainerProps> {
  componentDidMount() {
    // eslint-disable-next-line react/destructuring-assignment
    this.props.getAllBadges();
  }

  render() {
    const { badges, shortBadgesList } = this.props;

    return (
      <BadgeBrowseList shortBadgesList={shortBadgesList} badges={badges} />
    );
  }
}

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getAllBadges }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(BadgesListContainer);
