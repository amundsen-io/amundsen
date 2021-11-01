// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { getBookmarks } from 'ducks/bookmark/reducer';
import { GetBookmarksRequest } from 'ducks/bookmark/types';

import { createUser } from 'ducks/user/reducer';
import { CreateUserRequest } from 'ducks/user/types';

// Msal imports
import { callMsGraph } from '../../utils/MsGraphApiCall';

interface DispatchFromProps {
  createUser: (user: any) => CreateUserRequest;
  getBookmarks: (userId: string) => GetBookmarksRequest;
}

export type PreloaderProps = DispatchFromProps;

export class Preloader extends React.Component<PreloaderProps> {
  componentDidMount() {
    // this.props.getLoggedInUser();
    callMsGraph().then((response) => {
      const user = {
        last_login: new Date().toUTCString(),
        name: response.displayName,
        mail: response.mail,
        id: response.id,
      };
      this.props.createUser(user);
      this.props.getBookmarks(response.mail);
    });
  }

  render() {
    return null;
  }
}

export const mapDispatchToProps = (dispatch) =>
  bindActionCreators({ createUser, getBookmarks }, dispatch);

export default connect<{}, DispatchFromProps>(
  null,
  mapDispatchToProps
)(Preloader);
