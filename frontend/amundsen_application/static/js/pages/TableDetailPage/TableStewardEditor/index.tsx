// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import { updateTableSteward } from 'ducks/tableMetadata/stewards/reducer';

import StewardEditor, {
  ComponentProps,
  DispatchFromProps,
  StateFromProps,
} from 'components/StewardEditor';

import { indexUsersEnabled } from 'config/config-utils';

export const mapStateToProps = (state: GlobalState) => {
  const stewardObj = state.tableMetadata.tableStewards.stewards;
  const items = Object.keys(stewardObj).reduce((obj, stewardId) => {
    const { profile_url, user_id, display_name } = stewardObj[stewardId];
    let profileLink = profile_url;
    let isExternalLink = true;
    if (indexUsersEnabled()) {
      isExternalLink = false;
      profileLink = `/user/${user_id}?source=owned_by`;
    }
    obj[stewardId] = {
      label: display_name,
      link: profileLink,
      isExternal: isExternalLink,
    };
    return obj;
  }, {});

  return {
    isLoading: state.tableMetadata.tableStewards.isLoading,
    itemProps: items,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ onUpdateList: updateTableSteward }, dispatch);

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(StewardEditor);
