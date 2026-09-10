/* eslint-disable no-alert */
// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { Meta } from '@storybook/react/types-6-0';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';

import AppConfig from 'config/config';

import { getMockRouterProps } from 'fixtures/mockRouter';
import globalState from 'fixtures/globalState';

import StorySection from 'components/StorySection';

import { NavBar } from '.';

const middlewares = [];
const mockStore = configureStore(middlewares);

AppConfig.logoTitle = 'Amundsen';
AppConfig.navLinks = [
  {
    label: 'Browse',
    href: '/browse',
    id: 'link2',
    target: '_blank',
    use_router: false,
  },
  {
    label: 'Docs',
    href: '/docs',
    id: 'link3',
    target: '_blank',
    use_router: false,
  },
];
AppConfig.indexUsers.enabled = true;
AppConfig.mailClientFeatures.feedbackEnabled = true;
AppConfig.productTour = {
  '/': [
    {
      isFeatureTour: false,
      isShownOnFirstVisit: true,
      isShownProgrammatically: true,
      steps: [
        {
          target: '.nav-bar-left #logo-icon',
          title: 'Welcome to Amundsen',
          content:
            'Hi!, welcome to Amundsen, your data discovery and catalog product!',
        },
        {
          target: '.search-bar-form .search-bar-input',
          title: 'Search for resources',
          content: 'Here you will search for the resources you are looking for',
        },
        {
          target: '.bookmark-list-header',
          title: 'Save your bookmarks',
          content:
            'Here you will see a list of the resources you have bookmarked',
        },
      ],
    },
  ],
  '/search': [
    {
      isFeatureTour: true,
      isShownOnFirstVisit: true,
      isShownProgrammatically: false,
      steps: [
        {
          target: '.nav-bar-left a',
          title: 'Title about the logo',
          content: 'Content about the step pointing to the logo',
        },
        {
          target: '.search-filter-section-header #column',
          title: 'Filters',
          content: 'Info about Filters',
        },
        {
          target: '#search-input',
          title: 'Search ranking',
          content: 'Search ranking information',
        },
      ],
    },
  ],
};

const NAVBAR_CONTAINER_WIDTH = 1160;
const routerProps = getMockRouterProps<any>(null, {
  pathname: '/',
});
const { loggedInUser } = globalState.user;
const basicState = { ...globalState };

basicState.search.search_term = '';
basicState.search.isLoading = true;

const decorators = [
  (storyFn: () => React.ReactNode) => (
    <BrowserRouter>
      <Provider store={mockStore(globalState)}>{storyFn()}</Provider>
    </BrowserRouter>
  ),
];

export const NavBarStory = (): React.ReactNode => {
  AppConfig.navTheme = 'dark';
  AppConfig.logoPath = null;
  AppConfig.navAppSuite = null;

  return (
    <StorySection
      title="with dark theme and no logo"
      width={NAVBAR_CONTAINER_WIDTH}
    >
      <NavBar {...routerProps} loggedInUser={loggedInUser} />
    </StorySection>
  );
};

NavBarStory.storyName = 'with default options';
NavBarStory.decorators = decorators;

export const NavBarLightStory = (): React.ReactNode => {
  AppConfig.navTheme = 'light';
  AppConfig.logoPath = null;
  AppConfig.navAppSuite = null;

  return (
    <StorySection
      title="with light theme and no logo"
      width={NAVBAR_CONTAINER_WIDTH}
    >
      <NavBar {...routerProps} loggedInUser={loggedInUser} />
    </StorySection>
  );
};

NavBarLightStory.storyName = 'with light theme';
NavBarLightStory.decorators = decorators;

export const NavBarCustomLogoStory = (): React.ReactNode => {
  AppConfig.navTheme = 'dark';
  AppConfig.logoPath = 'static/images/icons/logo-hive.svg';
  AppConfig.navAppSuite = null;

  return (
    <StorySection title="with custom logo" width={NAVBAR_CONTAINER_WIDTH}>
      <NavBar {...routerProps} loggedInUser={loggedInUser} />
    </StorySection>
  );
};

NavBarCustomLogoStory.storyName = 'with custom logo';
NavBarCustomLogoStory.decorators = decorators;

export const NavBarAppSuiteStory = (): React.ReactNode => {
  AppConfig.navTheme = 'dark';
  AppConfig.logoPath = null;
  AppConfig.navAppSuite = [
    {
      label: 'App One',
      id: 'appOne',
      href: 'https://www.lyft.com',
      target: '_blank',
    },
    {
      label: 'App Two',
      id: 'appTwo',
      href: 'https://www.amundsen.io/',
      iconPath: '/static/images/icons/amundsen-logo-dark.svg',
    },
  ];

  return (
    <StorySection title="with app suite links" width={NAVBAR_CONTAINER_WIDTH}>
      <NavBar {...routerProps} loggedInUser={loggedInUser} />
    </StorySection>
  );
};

NavBarAppSuiteStory.storyName = 'with app suite';
NavBarAppSuiteStory.decorators = decorators;

export default {
  title: 'Features/NavBar',
  component: NavBar,
  decorators: [],
} as Meta;
