import * as React from 'react';
import Avatar from 'react-avatar';
import { Link, NavLink } from 'react-router-dom';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import AppConfig from '../../../config/config';
import { GlobalState } from "../../ducks/rootReducer";
import { getCurrentUser } from "../../ducks/user/reducer";
import { CurrentUser, GetCurrentUserRequest } from "../../ducks/user/types";

import './styles.scss';

// Props
interface StateFromProps {
  currentUser: CurrentUser;
}

interface DispatchFromProps {
  getCurrentUser: () => GetCurrentUserRequest;
}

type NavBarProps = StateFromProps & DispatchFromProps;

// State
interface NavBarState {
  currentUser: CurrentUser;
}

class NavBar extends React.Component<NavBarProps, NavBarState> {
  constructor(props) {
    super(props);

    this.state = {
      currentUser: this.props.currentUser,
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const { currentUser } = nextProps;
    return { currentUser };
  }

  componentDidMount() {
    this.props.getCurrentUser();
  }

  render() {
    return (
      <div className="container-fluid">
        <div className="row">
          <div className="nav-bar">
            <div className="nav-bar-left">
              {
                AppConfig.logoPath &&
                <img className="logo-icon" src={AppConfig.logoPath} />
              }
              <Link to={`/`}>
                AMUNDSEN
              </Link>
            </div>
            <div className="nav-bar-right">
              {
                AppConfig.navLinks.map((link, index) => {
                  if (link.use_router) {
                    return <NavLink key={index} to={link.href} target={link.target}>{link.label}</NavLink>
                  }
                  return <a key={index} href={link.href} target={link.target}>{link.label}</a>
                })
              }
              {
                this.state.currentUser &&
                <Avatar name={this.state.currentUser.display_name} size={48} round={true}/>
              }
            </div>
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state: GlobalState) => {
  return {
    currentUser: state.user.currentUser,
  }
};

const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({ getCurrentUser }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(NavBar);
