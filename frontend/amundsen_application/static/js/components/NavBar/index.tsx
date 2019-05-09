import * as React from 'react';
import * as Avatar from 'react-avatar';
import { Link, NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import AppConfig from 'config/config';
import { LinkConfig } from 'config/config-types';
import { GlobalState } from 'ducks/rootReducer';
import { getLoggedInUser } from 'ducks/user/reducer';
import { LoggedInUser, GetLoggedInUserRequest } from 'ducks/user/types';
import { logClick } from "ducks/utilMethods";

import './styles.scss';

// Props
interface StateFromProps {
  loggedInUser: LoggedInUser;
}

interface DispatchFromProps {
  getLoggedInUser: () => GetLoggedInUserRequest;
}

export type NavBarProps = StateFromProps & DispatchFromProps;

export class NavBar extends React.Component<NavBarProps> {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    this.props.getLoggedInUser();
  }

  generateNavLinks(navLinks: LinkConfig[]) {
    return navLinks.map((link, index) => {
      if (link.use_router) {
        return <NavLink className="title-3" key={index} to={link.href} target={link.target}
                        onClick={logClick}>{link.label}</NavLink>
      }
      return <a className="title-3" key={index} href={link.href} target={link.target}
                onClick={logClick}>{link.label}</a>
    });
  }

  render() {
    return (
      <div className="container-fluid">
        <div className="row">
          <div className="nav-bar">
            <div id="nav-bar-left" className="nav-bar-left">
              {
                AppConfig.logoPath &&
                <img id="logo-icon" className="logo-icon" src={AppConfig.logoPath} />
              }
              <Link to={`/`} className="title-3">
                AMUNDSEN
              </Link>
            </div>
            <div id="nav-bar-right" className="nav-bar-right">
              {this.generateNavLinks(AppConfig.navLinks)}
              {
                // TODO PEOPLE - Add link to user profile
                this.props.loggedInUser &&
                <div id="nav-bar-avatar">
                  <Avatar name={this.props.loggedInUser.display_name} size={32} round={true} />
                </div>
              }
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    loggedInUser: state.user.loggedInUser,
  }
};

export const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({ getLoggedInUser }, dispatch);
};

export default withRouter(connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(NavBar));
