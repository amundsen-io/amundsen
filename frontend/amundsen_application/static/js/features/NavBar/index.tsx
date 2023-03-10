/* eslint-disable no-debugger */
// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import * as Avatar from 'react-avatar';
import { RouteComponentProps } from 'react-router';
import { Link, NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { Binoculars, GridIcon } from 'components/SVGIcons';

import { LinkConfig, TourConfig } from 'config/config-types';
import {
  getLogoPath,
  feedbackEnabled,
  indexUsersEnabled,
  getNavLinks,
  getNavTheme,
  getLogoTitle,
  getProductToursFor,
  getNavAppSuite,
} from 'config/config-utils';

import { GlobalState } from 'ducks/rootReducer';

import { LoggedInUser } from 'interfaces';

import { logClick, logAction } from 'utils/analytics';

import Feedback from 'features/Feedback';
import SearchBar from 'features/SearchBar';
import { Tour } from 'components/Tour';

import './styles.scss';

const NUM_CHARS_FOR_KEY = 9;
const COLOR_LIGHT = '#ffffff';
const COLOR_DARK = '#292936'; // gray100
const DEFAULT_PAGE_TOUR_KEY = 'default-key';
const DEFAULT_FEATURE_TOUR_KEY = 'default-feature-key';
const PROFILE_LINK_TEXT = 'My Profile';
const PRODUCT_TOUR_BUTTON_TEXT = 'Discover Amundsen';
const APP_SUITE_BUTTON_TEXT = 'Related Apps';
export const HOMEPAGE_PATH = '/';
const AVATAR_SIZE = 32;

const GENERIC_LIGHT_LOGO_PATH = '/static/images/icons/amundsen-logo-light.svg';
const GENERIC_DARK_LOGO_PATH = '/static/images/icons/amundsen-logo-dark.svg';
const TRACKING_MESSAGES = {
  START_TOUR: 'Start Tour',
  END_TOUR: 'End Tour',
  NEXT_TOUR_STEP: 'Next Tour Step',
  CLOSE_TOUR: 'Tour Closed',
  OPEN_APP_SUITE: 'Open App Suite Menu',
  CLOSE_APP_SUITE: 'Close App Suite Menu',
  followAppSuiteLink: (label: string) => `Follow App Suite Link: ${label}`,
};

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
  theme: 'dark' | 'light';
};

export const ProductTourButton: React.FC<ProductTourButtonProps> = ({
  onClick,
  theme,
}) => (
  <button
    className="btn btn-nav-bar-icon btn-flat-icon"
    type="button"
    onClick={onClick}
  >
    <Binoculars fill={theme === 'dark' ? COLOR_LIGHT : COLOR_DARK} />
    <span className="sr-only">{PRODUCT_TOUR_BUTTON_TEXT}</span>
  </button>
);

type AppSuiteMenuProps = {
  onClick: (isOpen: boolean) => void;
  onItemClick?: (itemLabel: string) => void;
  theme: 'dark' | 'light';
};

export const AppSuiteMenu: React.FC<AppSuiteMenuProps> = ({
  onClick,
  onItemClick,
  theme,
}) => {
  const appList = getNavAppSuite();

  if (appList?.length === 0) {
    return null;
  }

  const handleItemClick = (_, e: React.MouseEvent) => {
    onItemClick?.((e.target as HTMLAnchorElement).text);
  };

  return (
    <Dropdown
      id="app-suite-dropdown"
      pullRight
      onToggle={onClick}
      onSelect={handleItemClick}
    >
      <Dropdown.Toggle noCaret className="btn btn-nav-bar-icon btn-flat-icon">
        <GridIcon fill={theme === 'dark' ? COLOR_LIGHT : COLOR_DARK} />
        <span className="sr-only">{APP_SUITE_BUTTON_TEXT}</span>
      </Dropdown.Toggle>
      <Dropdown.Menu className="app-suite-menu">
        {appList?.map(({ label, id, href, target, iconPath }) => (
          <MenuItem
            key={id}
            className="app-suite-link"
            href={href}
            target={target}
          >
            {iconPath && (
              <img className="app-suite-logo" src={iconPath} alt="" />
            )}
            {label}
          </MenuItem>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};

const generateNavLinks = (navLinks: LinkConfig[]) =>
  navLinks.map((link, index) => {
    if (link.use_router) {
      return (
        <NavLink
          className="nav-bar-link"
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
        className="nav-bar-link"
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

const getPageTourInfo = (pathname: string) => {
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

const getFeatureTourInfo = (pathname: string) => {
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

export const Logo: React.FC = () => {
  const defaultLogo =
    getNavTheme() === 'light'
      ? GENERIC_DARK_LOGO_PATH
      : GENERIC_LIGHT_LOGO_PATH;

  return (
    <Link className="logo-link" to="/" onClick={logClick}>
      <img
        id="logo-icon"
        className="logo-icon"
        src={getLogoPath() || defaultLogo}
        alt=""
      />
      <span className="logo-text">{getLogoTitle()}</span>
    </Link>
  );
};

type ProfileMenuProps = {
  loggedInUser: LoggedInUser;
};

export const ProfileMenu: React.FC<ProfileMenuProps> = ({ loggedInUser }) => {
  // eslint-disable-next-line @typescript-eslint/naming-convention
  const { user_id, display_name, email } = loggedInUser;
  const userLink = `/user/${user_id}?source=navbar`;

  let avatar = <div className="nav-shimmering-circle is-shimmer-animated" />;

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

  const handleAppSuiteToggle = (isOpen: boolean) => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: isOpen
        ? TRACKING_MESSAGES.OPEN_APP_SUITE
        : TRACKING_MESSAGES.CLOSE_APP_SUITE,
    });
  };

  const handleAppSuiteItemClick = (label: string) => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: TRACKING_MESSAGES.followAppSuiteLink(label),
    });
  };

  const handleTourClick = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: TRACKING_MESSAGES.START_TOUR,
    });
    setRunTour(true);
  };

  const handleTourEnd = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: TRACKING_MESSAGES.END_TOUR,
    });
    setRunTour(false);
  };

  const handleNextStep = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: TRACKING_MESSAGES.NEXT_TOUR_STEP,
    });
  };

  const handleTourClose = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: TRACKING_MESSAGES.CLOSE_TOUR,
    });
  };

  const theme = getNavTheme();
  const isLightTheme = theme === 'light';
  const hasAppSuite = getNavAppSuite() !== null;

  return (
    <nav className="container-fluid">
      <div className="row">
        <div className={`nav-bar ${isLightTheme && 'is-light'}`}>
          <div id="nav-bar-left" className="nav-bar-left">
            <Logo />
          </div>
          {renderSearchBar(pathname)}
          <div id="nav-bar-right" className="ml-auto nav-bar-right">
            {generateNavLinks(getNavLinks())}
            {hasPageTour && (
              <ProductTourButton theme={theme} onClick={handleTourClick} />
            )}
            {feedbackEnabled() && <Feedback theme={theme} />}
            {hasAppSuite && (
              <AppSuiteMenu
                theme={theme}
                onClick={handleAppSuiteToggle}
                onItemClick={handleAppSuiteItemClick}
              />
            )}
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
