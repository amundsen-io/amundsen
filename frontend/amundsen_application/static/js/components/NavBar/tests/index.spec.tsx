import * as React from 'react';
import * as Avatar from 'react-avatar';

import { shallow } from 'enzyme';

import { Link, NavLink } from 'react-router-dom';
import { NavBar, NavBarProps, mapStateToProps } from '../';

import { logClick } from "ducks/utilMethods";
jest.mock('ducks/utilMethods', () => {
  return jest.fn().mockImplementation(() => {
    return {logClick: jest.fn()};
  });
});

import AppConfig from 'config/config';
AppConfig.logoPath = '/test';
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
  }
];
AppConfig.indexUsers.enabled = true;


import globalState from 'fixtures/globalState';

describe('NavBar', () => {
  const setup = (propOverrides?: Partial<NavBarProps>) => {
    const props: NavBarProps = {
      loggedInUser: globalState.user.loggedInUser,
      ...propOverrides
    };
    const wrapper = shallow<NavBar>(<NavBar {...props} />);
    return { props, wrapper };
  };

  describe('generateNavLinks', () => {
    let content;
    beforeAll(() => {
      const { props, wrapper } = setup();
      content = wrapper.instance().generateNavLinks(AppConfig.navLinks);
    });

    it('returns a NavLink w/ correct props if user_router is true', () => {
      const expectedContent = JSON.stringify(
        <NavLink className="title-3" key={0} to='/announcements' target='_blank'
                 onClick={logClick}>Announcements</NavLink>
      );
      expect(JSON.stringify(content[0])).toEqual(expectedContent);
    });

    it('returns an anchor w/ correct props if user_router is false', () => {
      expect(shallow(content[1]).find('a').props()).toMatchObject({
        href: '/browse',
        target: '_blank',
      });
    });

    it('returns an anchor w/ correct test if user_router is false', () => {
      expect(shallow(content[1]).find('a').text()).toEqual('Browse');
    });
  });

  describe('render', () => {
    let element;
    let props;
    let wrapper;
    const spy = jest.spyOn(NavBar.prototype, 'generateNavLinks');
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders img with AppConfig.logoPath', () => {
      element = wrapper.find('img#logo-icon');
      expect(element.props()).toMatchObject({
        id: 'logo-icon',
        className: 'logo-icon',
        src: AppConfig.logoPath,
      });
    });

    it('renders homepage Link with correct path ', () => {
      element = wrapper.find('#nav-bar-left').find(Link);
      expect(element.props().to).toEqual('/');
    });

    it('renders homepage Link with correct text', () => {
      element = wrapper.find('#nav-bar-left').find(Link).find('.title-3');
      expect(element.children().text()).toEqual('AMUNDSEN');
    });

    it('calls generateNavLinks with correct props', () => {
      expect(spy).toHaveBeenCalledWith(AppConfig.navLinks);
    });

    it('renders Avatar for loggedInUser', () => {
      expect(wrapper.find(Avatar).props()).toMatchObject({
        name: props.loggedInUser.display_name,
        size: 32,
        round: true,
      })
    });

    it('renders a Link to the user profile if `indexUsers` is enabled', () => {
      expect(wrapper.find('#nav-bar-avatar-link').exists()).toBe(true)
    });

    it('does not render a Link to the user profile if `indexUsers` is disabled', () => {
      AppConfig.indexUsers.enabled = false;
      const { wrapper } = setup();
      expect(wrapper.find('#nav-bar-avatar-link').exists()).toBe(false)
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
