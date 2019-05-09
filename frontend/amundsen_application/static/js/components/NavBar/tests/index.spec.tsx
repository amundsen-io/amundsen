import * as React from 'react';
import * as Avatar from 'react-avatar';

import { shallow } from 'enzyme';

import { Link, NavLink } from 'react-router-dom';
import { NavBar, NavBarProps, mapDispatchToProps, mapStateToProps } from '../';

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

import globalState from 'fixtures/globalState';

describe('NavBar', () => {
  const setup = (propOverrides?: Partial<NavBarProps>) => {
    const props: NavBarProps = {
      loggedInUser: globalState.user.loggedInUser,
      getLoggedInUser: jest.fn(),
      ...propOverrides
    };
    const wrapper = shallow<NavBar>(<NavBar {...props} />);
    return { props, wrapper };
  };

  describe('componentDidMount', () => {
    it('calls props.getLoggedInUser', () => {
      const { props, wrapper } = setup();
      wrapper.instance().componentDidMount();
      expect(props.getLoggedInUser).toHaveBeenCalled();
    });
  });

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
      element = wrapper.find('#nav-bar-left').find(Link);
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
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;

  beforeEach(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets getLoggedInUser on the props', () => {
    expect(result.getLoggedInUser).toBeInstanceOf(Function);
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
