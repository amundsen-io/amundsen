// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import * as Avatar from 'react-avatar';
import { RouteComponentProps } from 'react-router';
import { Link, NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { Binoculars } from 'components/SVGIcons';

import { LinkConfig, TourConfig } from 'config/config-types';
import {
  getLogoPath,
  feedbackEnabled,
  indexUsersEnabled,
  getNavLinks,
  getLogoTitle,
  getProductToursFor,
} from 'config/config-utils';

import { GlobalState } from 'ducks/rootReducer';

import { LoggedInUser } from 'interfaces';

import { logClick, logAction } from 'utils/analytics';

import Feedback from 'features/Feedback';
import SearchBar from 'features/SearchBar';
import { Tour } from 'components/Tour';

import './styles.scss';

const NUM_CHARS_FOR_KEY = 9;
const COLOR_WHITE = '#ffffff';
const DEFAULT_PAGE_TOUR_KEY = 'default-key';
const DEFAULT_FEATURE_TOUR_KEY = 'default-feature-key';
const PROFILE_LINK_TEXT = 'My Profile';
const PRODUCT_TOUR_BUTTON_TEXT = 'Discover Amundsen';
export const HOMEPAGE_PATH = '/';
const AVATAR_SIZE = 32;

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
          className="text-title-w3 border-bottom-white"
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
        className="text-title-w3 border-bottom-white"
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

const renderSearchBar = (pathname: string) => {
  if (pathname !== HOMEPAGE_PATH) {
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
  const { result: productToursForThisPage, tourPath } =
    getProductToursFor(pathname);
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
  const { result: productToursForThisPage, tourPath } =
    getProductToursFor(pathname);
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

export const Logo: React.FC = () => (
  <Link to="/" onClick={logClick}>
    {getLogoPath() && (
      <img
        id="logo-icon"
        className="logo-icon"
        src={getLogoPath() || ''}
        alt=""
      />
    )}
    <span className="text-title-w3">{getLogoTitle()}</span>
  </Link>
);

type ProfileMenuProps = {
  loggedInUser: LoggedInUser;
};

export const ProfileMenu: React.FC<ProfileMenuProps> = ({ loggedInUser }) => {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  const { user_id, display_name, email } = loggedInUser;
  const userLink = `/user/${user_id}?source=navbar`;

  let avatar = <div className="shimmering-circle is-shimmer-animated" />;

  if (display_name) {
    avatar = <Avatar name={display_name} size={AVATAR_SIZE} round />;
  }

  if (!indexUsersEnabled()) {
    return <div className="nav-bar-avatar">{avatar}</div>;
  }

  return (
    <Dropdown id="user-dropdown" pullRight>
      <Dropdown.Toggle noCaret className="nav-bar-avatar avatar-dropdown">
        {avatar}
      </Dropdown.Toggle>
      <Dropdown.Menu className="profile-menu">
        <div className="profile-menu-header">
          <div className="title-2">{display_name}</div>
          <div>{email}</div>
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
  );
};

// Props
interface StateFromProps {
  loggedInUser: LoggedInUser;
}

export type NavBarProps = StateFromProps & RouteComponentProps<{}>;

export const NavBar: React.FC<NavBarProps> = ({ loggedInUser, location }) => {
  const [runTour, setRunTour] = React.useState(false);
  const { pathname } = location;
  const { hasPageTour, pageTourKey, pageTourSteps } = getPageTourInfo(pathname);
  const { hasFeatureTour, featureTourKey, featureTourSteps } =
    getFeatureTourInfo(pathname);

  React.useEffect(() => {
    setRunTour(false);
  }, [pathname]);

  const handleTourClick = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'Start Tour',
    });
    setRunTour(true);
  };

  const handleTourEnd = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'End Tour',
    });
    setRunTour(false);
  };

  const handleNextStep = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'Next Tour Step',
    });
  };

  const handleTourClose = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'Tour Closed',
    });
  };

  return (
    <nav className="container-fluid">
      <div className="row">
        <div className="nav-bar">
          <div id="nav-bar-left" className="nav-bar-left">
            <Logo />
          </div>
          {renderSearchBar(pathname)}
          <div id="nav-bar-right" className="ml-auto nav-bar-right">
            {generateNavLinks(getNavLinks())}
            {hasPageTour && <ProductTourButton onClick={handleTourClick} />}
            {feedbackEnabled() && <Feedback />}
            {loggedInUser && <ProfileMenu loggedInUser={loggedInUser} />}
          </div>
        </div>
        {(hasPageTour || hasFeatureTour) && (
          <Tour
            run={runTour}
            steps={hasPageTour ? pageTourSteps : featureTourSteps}
            onTourEnd={handleTourEnd}
            onTourClose={handleTourClose}
            onNextStep={handleNextStep}
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
