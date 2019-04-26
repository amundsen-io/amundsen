import * as React from 'react';
import { shallow } from 'enzyme';

import Avatar from 'react-avatar';
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
    let props: NavBarProps;
    let subject;

    beforeEach(() => {
        props = {
          loggedInUser:  {
            user_id: 'test0',
            display_name: 'Test User',
          },
          getLoggedInUser: jest.fn(),
        };
        subject = shallow(<NavBar {...props} />);
    });

    describe('componentDidMount', () => {
        it('calls props.getLoggedInUser', () => {
            subject.instance().componentDidMount();
            expect(props.getLoggedInUser).toHaveBeenCalled();
        });
    });

    describe('generateNavLinks', () => {
        let content;
        beforeEach(() => {
            content = subject.instance().generateNavLinks(AppConfig.navLinks);
        });

        it('returns a NavLink w/ correct props if user_router is true', () => {
            const expectedContent = JSON.stringify(<NavLink key={0} to='/announcements' target='_blank' onClick={logClick}>Announcements</NavLink>);
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
        const spy = jest.spyOn(NavBar.prototype, 'generateNavLinks');
        it('renders img with AppConfig.logoPath', () => {
            element = subject.find('img#logo-icon');
            expect(element.props()).toMatchObject({
              id: 'logo-icon',
              className: 'logo-icon',
              src: AppConfig.logoPath,
            });
        });

        it('renders homepage Link with correct path ', () => {
            element = subject.find('#nav-bar-left').find(Link);
            expect(element.props().to).toEqual('/');
        });

        it('renders homepage Link with correct text', () => {
            element = subject.find('#nav-bar-left').find(Link);
            expect(element.children().text()).toEqual('AMUNDSEN');
        })

        it('calls generateNavLinks with correct props', () => {
            expect(spy).toHaveBeenCalledWith(AppConfig.navLinks);
        });

        it('renders Avatar for loggedInUser', () => {
            /* Note: subject.find(Avatar) does not work - workaround is to directly check the content */
            const expectedContent = <Avatar name={props.loggedInUser.display_name} size={32} round={true} />;
            expect(subject.find('#nav-bar-avatar').props().children).toEqual(expectedContent);
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
