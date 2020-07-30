// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import Flag, { FlagProps } from 'components/common/Flag';
import { ResourceType } from 'interfaces';
import { updateSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { logClick } from 'ducks/utilMethods';

import './styles.scss';

export interface DispatchFromProps {
  searchBadge: (badgeText: string) => UpdateSearchStateRequest;
}

export type ClickableBadgeProps = FlagProps & DispatchFromProps;

export class ClickableBadge extends React.Component<ClickableBadgeProps> {
  onClick = (e) => {
    const badgeText = this.props.text;
    logClick(e, {
      target_type: 'badge',
      label: badgeText,
    });
    this.props.searchBadge(badgeText);
  };

  render() {
    return (
      <span className="clickable-badge" onClick={this.onClick}>
        <Flag
          caseType={this.props.caseType}
          text={this.props.text}
          labelStyle={this.props.labelStyle}
        />
      </span>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators(
    {
      searchBadge: (badgeText: string) =>
        updateSearchState({
          filters: {
            [ResourceType.table]: { badges: badgeText },
          },
          submitSearch: true,
        }),
    },
    dispatch
  );
};

export default connect<null, DispatchFromProps, FlagProps>(
  null,
  mapDispatchToProps
)(ClickableBadge);
