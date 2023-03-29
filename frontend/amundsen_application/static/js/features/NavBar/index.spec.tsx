// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as History from 'history';
import { shallow, mount } from 'enzyme';
import { Link } from 'react-router-dom';

import { getMockRouterProps } from 'fixtures/mockRouter';

import Feedback from 'features/Feedback';
import { Tour } from 'components/Tour';

import AppConfig from 'config/config';
import globalState from 'fixtures/globalState';

import {
  NavBar,
  Logo,
  ProfileMenu,
  NavBarProps,
  ProductTourButton,
  AppSuiteMenu,
  mapStateToProps,
  HOMEPAGE_PATH,
} from '.';

jest.mock('ducks/utilMethods', () =>
  jest.fn().mockImplementation(() => ({ logClick: jest.fn() }))
);

AppConfig.logoPath = '/test';
AppConfig.logoTitle = 'test';
AppConfig.navLinks = [
  {
    label: 'Announcements',
    href: '/announcements',
    id: 'link1',
    target: '_blank',
    use_router: true,
  },
  {
    label: 'Browse',
    href: '/browse',
    id: 'link2',
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
          content: 'Content about the step pointing to the log',
        },
        {
          target: '.search-filter-section-header #column',
          title: 'Filters',
          content: 'Info about Filters',
        },
        {
          target: '#search-input',
          title: 'Search ranking',
          content: 'Search raking information',
        },
      ],
    },
  ],
};

const setup = (
  propOverrides?: Partial<NavBarProps>,
  location?: Partial<History.Location>
) => {
  const routerProps = getMockRouterProps<any>(null, location);
  const props: NavBarProps = {
    loggedInUser: globalState.user.loggedInUser,
    ...routerProps,
    ...propOverrides,
  };
  const wrapper = shallow<NavBarProps>(<NavBar {...props} />);

  return { props, wrapper };
};

describe('NavBar', () => {
  describe('render', () => {
    let props;
    let wrapper;

    beforeAll(() => {
      ({ props, wrapper } = setup());
    });

    it('renders Logo component', () => {
      expect(wrapper.find(Logo).exists()).toBe(true);
    });

    it('renders Feedback component', () => {
      expect(wrapper.find(Feedback).exists()).toBe(true);
    });

    it('renders ProfileMenu for loggedInUser', () => {
      expect(wrapper.find(ProfileMenu).props()).toMatchObject({
        loggedInUser: props.loggedInUser,
      });
    });

    describe('when not in the homepage', () => {
      it('does render the search bar', () => {
        const { wrapper } = setup(undefined, {
          pathname: '/announcements',
        });
        const expected = 1;
        const actual = wrapper.find('.nav-search-bar').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when in a page with a page tour', () => {
      it('does not render the search bar', () => {
        const { wrapper } = setup(undefined, { pathname: '/' });
        const expected = 0;
        const actual = wrapper.find('.nav-search-bar').length;

        expect(actual).toEqual(expected);
      });

      it('should show the tour start button', () => {
        const { wrapper } = setup(undefined, { pathname: '/' });
        const expected = 1;
        const actual = wrapper.find(ProductTourButton).length;

        expect(actual).toEqual(expected);
      });

      it('should render the tour component', () => {
        const { wrapper } = setup(undefined, { pathname: '/' });
        const expected = 1;
        const actual = wrapper.find(Tour).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when in a page with a feature tour', () => {
      it('should render the tour component', () => {
        const { wrapper } = setup(undefined, { pathname: '/search' });
        const expected = 1;
        const actual = wrapper.find(Tour).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when in a page without a page tour', () => {
      it('should not render tour start button', () => {
        const { wrapper } = setup(undefined, { pathname: '/announcements' });
        const expected = 0;
        const actual = wrapper.find(ProductTourButton).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when light theme', () => {
      it('should add the is-light class', () => {
        AppConfig.navTheme = 'light';

        const { wrapper } = setup();
        const expected = 1;
        const actual = wrapper.find('.nav-bar.is-light').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when nav app suite', () => {
      it('should add the icon button', () => {
        AppConfig.navAppSuite = [
          {
            label: 'Lyft Homepage',
            id: 'lyft',
            href: 'https://www.lyft.com',
            target: '_blank',
            iconPath: '/static/images/lyft-logo.svg',
          },
          {
            label: 'Amundsen Docs',
            id: 'ams-docs',
            href: 'https://www.amundsen.io/',
            iconPath: '/static/images/ams-logo.svg',
          },
        ];

        const { wrapper } = setup();
        const expected = 1;
        const actual = wrapper.find(AppSuiteMenu).length;

        expect(actual).toEqual(expected);
      });
    });
  });

  describe('lifetime', () => {
    describe('when clicking on the Product Tour button', () => {
      it('should call its handler', () => {
        const handlerSpy = jest.fn();
        const wrapper = mount(
          <ProductTourButton theme="dark" onClick={handlerSpy} />
        );
        const expected = 1;

        wrapper.find(ProductTourButton).simulate('click');

        const actual = (handlerSpy as jest.Mock).mock.calls.length;

        expect(actual).toEqual(expected);
      });
    });
  });
});

const logoSetup = () => {
  const wrapper = shallow(<Logo />);

  return { wrapper };
};

describe('Logo', () => {
  describe('render', () => {
    it('renders img with AppConfig.logoPath', () => {
      const { wrapper } = logoSetup();

      expect(wrapper.find('img#logo-icon').props()).toMatchObject({
        id: 'logo-icon',
        className: 'logo-icon',
        src: AppConfig.logoPath,
      });
    });

    it('renders homepage Link with correct path', () => {
      const { wrapper } = logoSetup();
      const expected = HOMEPAGE_PATH;
      const actual = wrapper.find(Link).prop('to');

      expect(actual).toEqual(expected);
    });

    it('renders homepage Link with correct text', () => {
      const { wrapper } = logoSetup();
      const expected = 'test';
      const actual = wrapper.find(Link).find('.logo-text').children().text();

      expect(actual).toEqual(expected);
    });
  });
});

describe('mapStateToProps', () => {
  it('sets loggedInUser on the props', () => {
    const result = mapStateToProps(globalState);

    expect(result.loggedInUser).toEqual(globalState.user.loggedInUser);
  });
});
