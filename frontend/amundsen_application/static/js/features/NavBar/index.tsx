// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as Avatar from 'react-avatar';
import { RouteComponentProps } from 'react-router';
import { Link, NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { Dropdown, MenuItem } from 'react-bootstrap';

import AppConfig from 'config/config';
import { LinkConfig, TourConfig } from 'config/config-types';
import {
  feedbackEnabled,
  indexUsersEnabled,
  getNavLinks,
  getLogoTitle,
  getProductToursFor,
} from 'config/config-utils';

import { GlobalState } from 'ducks/rootReducer';

import { LoggedInUser } from 'interfaces';

import { logClick } from 'utils/analytics';

import Feedback from 'features/Feedback';
import SearchBar from 'components/SearchBar';

import './styles.scss';

const PROFILE_LINK_TEXT = 'My Profile';
const PRODUCT_TOUR_BUTTON_TEXT = 'Discover Amundsen';
export const HOMEPAGE_PATH = '/';

/**
 * Gets the paths of pages with page tours
 */
const reduceToPageTours = (acc: string[], tour: TourConfig) => {
  if (!tour.isFeatureTour) {
    return [...acc, tour];
  }

  return acc;
};

type ProductTourButtonProps = {
  onClick: () => void;
};

export const ProductTourButton: React.FC<ProductTourButtonProps> = ({
  onClick,
}: ProductTourButtonProps) => (
  <button
    className="btn product-tour-btn btn-flat-icon"
    type="button"
    onClick={onClick}
  >
    <img className="icon" src="static/images/icons/dashboard.svg" alt="" />
    <span className="sr-only">{PRODUCT_TOUR_BUTTON_TEXT}</span>
  </button>
);

// Props
interface StateFromProps {
  loggedInUser: LoggedInUser;
}

export type NavBarProps = StateFromProps & RouteComponentProps<{}>;

export class NavBar extends React.Component<NavBarProps> {
  handleTourClick = () => {
    console.log('click!');
    // Set state
  };

  generateNavLinks(navLinks: LinkConfig[]) {
    return navLinks.map((link, index) => {
      if (link.use_router) {
        return (
          <NavLink
            className="title-3 border-bottom-white"
            key={index}
            to={link.href}
            target={link.target}
            onClick={logClick}
          >
            {link.label}
          </NavLink>
        );
      }
      return (
        <a
          className="title-3 border-bottom-white"
          key={index}
          href={link.href}
          target={link.target}
          onClick={logClick}
        >
          {link.label}
        </a>
      );
    });
  }

  renderSearchBar = () => {
    const { location } = this.props;

    if (location.pathname !== HOMEPAGE_PATH) {
      return (
        <div className="nav-search-bar">
          <SearchBar size="small" />
        </div>
      );
    }
    return null;
  };

  render() {
    const { loggedInUser, location } = this.props;
    const productToursForThisPage = getProductToursFor(location.pathname);
    const pageTours = productToursForThisPage
      ? productToursForThisPage.reduce(reduceToPageTours, [])
      : [];
    const hasPageTour = productToursForThisPage ? !!pageTours.length : false;
    const userLink = `/user/${loggedInUser.user_id}?source=navbar`;
    let avatar = <div className="shimmering-circle is-shimmer-animated" />;

    if (loggedInUser.display_name) {
      avatar = <Avatar name={loggedInUser.display_name} size={32} round />;
    }

    return (
      <nav className="container-fluid">
        <div className="row">
          <div className="nav-bar">
            <div id="nav-bar-left" className="nav-bar-left">
              <Link to="/">
                {AppConfig.logoPath && (
                  <img
                    id="logo-icon"
                    className="logo-icon"
                    src={AppConfig.logoPath}
                    alt=""
                  />
                )}
                <span className="title-3">{getLogoTitle()}</span>
              </Link>
            </div>
            {this.renderSearchBar()}
            <div id="nav-bar-right" className="ml-auto nav-bar-right">
              {this.generateNavLinks(getNavLinks())}
              {hasPageTour && (
                <ProductTourButton onClick={this.handleTourClick} />
              )}
              {feedbackEnabled() && <Feedback />}
              {loggedInUser && indexUsersEnabled() && (
                <Dropdown id="user-dropdown" pullRight>
                  <Dropdown.Toggle
                    noCaret
                    className="nav-bar-avatar avatar-dropdown"
                  >
                    {avatar}
                  </Dropdown.Toggle>
                  <Dropdown.Menu className="profile-menu">
                    <div className="profile-menu-header">
                      <div className="title-2">{loggedInUser.display_name}</div>
                      <div>{loggedInUser.email}</div>
                    </div>
                    <MenuItem
                      componentClass={Link}
                      id="nav-bar-avatar-link"
                      to={userLink}
                      href={userLink}
                    >
                      {PROFILE_LINK_TEXT}
                    </MenuItem>
                  </Dropdown.Menu>
                </Dropdown>
              )}
              {loggedInUser && !indexUsersEnabled() && (
                <div className="nav-bar-avatar">{avatar}</div>
              )}
            </div>
          </div>
        </div>
      </nav>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  loggedInUser: state.user.loggedInUser,
});

export default connect<StateFromProps>(mapStateToProps)(withRouter(NavBar));
