import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { getBookmarks } from "ducks/bookmark/reducer";
import { GetBookmarksRequest } from "ducks/bookmark/types";

import { getLoggedInUser } from "ducks/user/reducer";
import { GetLoggedInUserRequest } from "ducks/user/types";

interface DispatchFromProps {
  getLoggedInUser: () => GetLoggedInUserRequest;
  getBookmarks: () => GetBookmarksRequest;
}

export type PreloaderProps = DispatchFromProps;

export class Preloader extends React.Component<PreloaderProps>{
  constructor(props) {
    super(props)
  }

  componentDidMount() {
    this.props.getLoggedInUser();
    this.props.getBookmarks();
  }

  render() { return null; }
}

export const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({ getLoggedInUser, getBookmarks }, dispatch);
};

export default connect<{}, DispatchFromProps>(null, mapDispatchToProps)(Preloader);
