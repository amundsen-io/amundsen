import * as React from 'react';
import * as Avatar from 'react-avatar';
import { Link, NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';

import AppConfig from 'config/config';
import { LinkConfig } from 'config/config-types';
import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'ducks/utilMethods';

import { LoggedInUser } from 'interfaces';

import './styles.scss';

// Props
interface StateFromProps {
  loggedInUser: LoggedInUser;
}

export type NavBarProps = StateFromProps;

export class NavBar extends React.Component<NavBarProps> {
  constructor(props) {
    super(props);
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
              <Link to={`/`}>
                {
                  AppConfig.logoPath &&
                  <img id="logo-icon" className="logo-icon" src={AppConfig.logoPath} />
                }
                <span className="title-3">AMUNDSEN</span>
              </Link>
            </div>
            <div id="nav-bar-right" className="nav-bar-right">
              {this.generateNavLinks(AppConfig.navLinks)}
              {
                this.props.loggedInUser && AppConfig.indexUsers.enabled &&
                <Link id="nav-bar-avatar-link" to={`/user/${this.props.loggedInUser.user_id}`}>
                  <div id="nav-bar-avatar">
                    <Avatar name={this.props.loggedInUser.display_name} size={32} round={true} />
                  </div>
                </Link>
              }
              {
                this.props.loggedInUser && !AppConfig.indexUsers.enabled &&
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

export default withRouter(connect<StateFromProps>(mapStateToProps)(NavBar));
