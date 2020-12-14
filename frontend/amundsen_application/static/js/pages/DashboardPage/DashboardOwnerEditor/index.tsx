// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';

import OwnerEditor, {
  ComponentProps,
  StateFromProps,
  OwnerItemProps,
} from 'components/OwnerEditor';

import { User } from 'interfaces';

import { indexUsersEnabled } from 'config/config-utils';

export const DASHBOARD_OWNER_SOURCE = 'dashboard_page_owner';

const convertDashboardOwners = (owners: User[]): OwnerItemProps =>
  owners.reduce((obj, user) => {
    const { profile_url, user_id, display_name } = user;
    let profileLink = profile_url;
    let isExternalLink = true;
    if (indexUsersEnabled()) {
      isExternalLink = false;
      profileLink = `/user/${user_id}?source=${DASHBOARD_OWNER_SOURCE}`;
    }
    obj[user_id] = {
      label: display_name,
      link: profileLink,
      isExternal: isExternalLink,
    };
    return obj;
  }, {});

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: false,
  itemProps: convertDashboardOwners(state.dashboard.dashboard.owners),
});

export default connect<StateFromProps, {}, ComponentProps>(
  mapStateToProps,
  {}
)(OwnerEditor);
