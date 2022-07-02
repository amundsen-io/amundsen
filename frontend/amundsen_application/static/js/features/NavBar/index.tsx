// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import * as Avatar from 'react-avatar';
import { RouteComponentProps } from 'react-router';
import { Link, NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { Binoculars } from 'components/SVGIcons';

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
import { Tour } from 'components/Tour';

import './styles.scss';

const NUM_CHARS_FOR_KEY = 9;
const COLOR_WHITE = '#ffffff';
const DEFAULT_PAGE_TOUR_KEY = 'default-key';
const DEFAULT_FEATURE_TOUR_KEY = 'default-feature-key';
const PROFILE_LINK_TEXT = 'My Profile';
const PRODUCT_TOUR_BUTTON_TEXT = 'Discover Amundsen';
export const HOMEPAGE_PATH = '/';

/**
 * Gets the paths of pages with page tours
 */
const reduceToPageTours = (acc: TourConfig[], tour: TourConfig) => {
  if (!tour.isFeatureTour) {
    return [...acc, tour];
  }

  return acc;
};

/**
 * Gets the paths of pages with feature tours
 */
const reduceToFeatureTours = (acc: TourConfig[], tour: TourConfig) => {
  if (tour.isFeatureTour) {
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
    className="btn btn-nav-bar-icon btn-flat-icon"
    type="button"
    onClick={onClick}
  >
    <Binoculars fill={COLOR_WHITE} />
    <span className="sr-only">{PRODUCT_TOUR_BUTTON_TEXT}</span>
  </button>
);

const generateNavLinks = (navLinks: LinkConfig[]) =>
  navLinks.map((link, index) => {
    if (link.use_router) {
      return (
        <NavLink
          className="title-3 border-bottom-white"
          key={index}
          to={link.href}
          target={link.target}
          onClick={logClick}
          data-test={`link-to-${link.label}`}
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
        data-test={`link-to-${link.label}`}
      >
        {link.label}
      </a>
    );
  });

const renderSearchBar = (location) => {
  if (location.pathname !== HOMEPAGE_PATH) {
    return (
      <div className="nav-search-bar">
        <SearchBar size="small" />
      </div>
    );
  }
  return null;
};

const generateKeyFromSteps = (tourSteps: TourConfig[], pathname: string) =>
  tourSteps.length
    ? `${tourSteps[0].steps[0].content.substring(
        0,
        NUM_CHARS_FOR_KEY
      )}-path:${pathname}`
    : false;

const getPageTourInfo = (pathname) => {
  const { result: productToursForThisPage, tourPath } = getProductToursFor(
    pathname
  );
  const pageTours = productToursForThisPage
    ? productToursForThisPage.reduce(reduceToPageTours, [])
    : [];
  const pageTourSteps = pageTours.length ? pageTours[0].steps : [];
  const pageTourKey =
    generateKeyFromSteps(pageTours, tourPath) || DEFAULT_PAGE_TOUR_KEY;
  const hasPageTour = productToursForThisPage ? !!pageTours.length : false;

  return { hasPageTour, pageTourKey, pageTourSteps };
};

const getFeatureTourInfo = (pathname) => {
  const { result: productToursForThisPage, tourPath } = getProductToursFor(
    pathname
  );
  const featureTours = productToursForThisPage
    ? productToursForThisPage.reduce(reduceToFeatureTours, [])
    : [];
  const featureTourSteps = featureTours.length ? featureTours[0].steps : [];
  const featureTourKey =
    generateKeyFromSteps(featureTours, tourPath) || DEFAULT_FEATURE_TOUR_KEY;
  const hasFeatureTour = productToursForThisPage
    ? !!featureTourSteps.length
    : false;

  return { hasFeatureTour, featureTourKey, featureTourSteps };
};

// Props
interface StateFromProps {
  loggedInUser: LoggedInUser;
}

export type NavBarProps = StateFromProps & RouteComponentProps<{}>;

export const NavBar: React.FC<NavBarProps> = ({ loggedInUser, location }) => {
  const [runTour, setRunTour] = React.useState(false);
  const { hasPageTour, pageTourKey, pageTourSteps } = getPageTourInfo(
    location.pathname
  );
  const {
    hasFeatureTour,
    featureTourKey,
    featureTourSteps,
  } = getFeatureTourInfo(location.pathname);

  React.useEffect(() => {
    setRunTour(false);
  }, [location.pathname]);

  const userLink = `/user/${loggedInUser.user_id}?source=navbar`;
  let avatar = <div className="shimmering-circle is-shimmer-animated" />;

  if (loggedInUser.display_name) {
    avatar = <Avatar name={loggedInUser.display_name} size={32} round />;
  }

  const handleTourClick = () => {
    setRunTour(true);
  };

  const handleTourEnd = () => {
    setRunTour(false);
  };

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
          {renderSearchBar(location)}
          <div id="nav-bar-right" className="ml-auto nav-bar-right">
            {generateNavLinks(getNavLinks())}
            {hasPageTour && <ProductTourButton onClick={handleTourClick} />}
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
        {(hasPageTour || hasFeatureTour) && (
          <Tour
            run={runTour}
            steps={hasPageTour ? pageTourSteps : featureTourSteps}
            onTourEnd={handleTourEnd}
            triggersOnFirstView
            key={hasPageTour ? pageTourKey : featureTourKey} // Re-renders tour on each page
            triggerFlagId={hasPageTour ? pageTourKey : featureTourKey}
          />
        )}
      </div>
    </nav>
  );
};

export const mapStateToProps = (state: GlobalState) => ({
  loggedInUser: state.user.loggedInUser,
});

export default connect<StateFromProps>(mapStateToProps)(withRouter(NavBar));
