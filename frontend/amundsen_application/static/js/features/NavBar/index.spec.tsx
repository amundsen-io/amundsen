// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as Avatar from 'react-avatar';
import * as History from 'history';
import { shallow, mount } from 'enzyme';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import { getMockRouterProps } from 'fixtures/mockRouter';

import Feedback from 'features/Feedback';
import { Tour } from 'components/Tour';

import AppConfig from 'config/config';

import globalState from 'fixtures/globalState';
import {
  NavBar,
  NavBarProps,
  ProductTourButton,
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
    let element;
    let props;
    let wrapper;

    beforeAll(() => {
      ({ props, wrapper } = setup());
    });

    it('renders img with AppConfig.logoPath', () => {
      element = wrapper.find('img#logo-icon');

      expect(element.props()).toMatchObject({
        id: 'logo-icon',
        className: 'logo-icon',
        src: AppConfig.logoPath,
      });
    });

    it('renders homepage Link with correct path', () => {
      const expected = HOMEPAGE_PATH;
      const actual = wrapper.find('#nav-bar-left').find(Link).props().to;

      expect(actual).toEqual(expected);
    });

    it('renders homepage Link with correct text', () => {
      const expected = 'test';
      const actual = wrapper
        .find('#nav-bar-left')
        .find(Link)
        .find('.title-3')
        .children()
        .text();

      expect(actual).toEqual(expected);
    });

    it('renders Feedback component', () => {
      expect(wrapper.find(Feedback).exists()).toBe(true);
    });

    it('renders Avatar for loggedInUser', () => {
      expect(wrapper.find(Avatar).props()).toMatchObject({
        name: props.loggedInUser.display_name,
        size: 32,
        round: true,
      });
    });

    describe('when indexUsers is enabled', () => {
      it('renders Avatar for loggedInUser inside of user dropdown', () => {
        expect(
          wrapper.find(Dropdown).find(Dropdown.Toggle).find(Avatar).props()
        ).toMatchObject({
          name: props.loggedInUser.display_name,
          size: 32,
          round: true,
        });
      });

      it('renders user dropdown header', () => {
        element = wrapper
          .find(Dropdown)
          .find(Dropdown.Menu)
          .find('.profile-menu-header');

        expect(element.children().at(0).text()).toEqual(
          props.loggedInUser.display_name
        );
        expect(element.children().at(1).text()).toEqual(
          props.loggedInUser.email
        );
      });

      it('renders My Profile link correctly inside of user dropdown', () => {
        element = wrapper
          .find(Dropdown)
          .find(Dropdown.Menu)
          .find(MenuItem)
          .at(0);

        expect(element.children().text()).toEqual('My Profile');
        expect(element.props().to).toEqual('/user/test0?source=navbar');
      });
    });

    describe('when indexUsers is disabled', () => {
      it('does not render a Link to the user profile', () => {
        AppConfig.indexUsers.enabled = false;
        const { wrapper } = setup();

        expect(wrapper.find('#nav-bar-avatar-link').exists()).toBe(false);
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
  });

  describe('lifetime', () => {
    describe('when clicking on the Product Tour button', () => {
      it('should call its handler', () => {
        const handlerSpy = jest.fn();
        const wrapper = mount(<ProductTourButton onClick={handlerSpy} />);
        const expected = 1;

        wrapper.find(ProductTourButton).simulate('click');

        const actual = (handlerSpy as jest.Mock).mock.calls.length;

        expect(actual).toEqual(expected);
      });
    });
  });
});

describe('mapStateToProps', () => {
  let result;

  beforeEach(() => {
    result = mapStateToProps(globalState);
  });

  it('sets loggedInUser on the props', () => {
    expect(result.loggedInUser).toEqual(globalState.user.loggedInUser);
  });
});
