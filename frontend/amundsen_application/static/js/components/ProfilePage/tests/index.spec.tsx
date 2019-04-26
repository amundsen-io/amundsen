import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import Avatar from 'react-avatar';

import { shallow } from 'enzyme';

import Breadcrumb from 'components/common/Breadcrumb';
import Flag from 'components/common/Flag';
import Tabs from 'components/common/Tabs';
import { ProfilePage, ProfilePageProps, mapDispatchToProps, mapStateToProps } from '../';

import globalState from 'fixtures/globalState';

describe('ProfilePage', () => {
    let props: ProfilePageProps;
    let subject;

    beforeEach(() => {
        props = {
          user:  {
            user_id: 'test0',
            display_name: 'Test User',
            email: 'test@test.com',
            github_name: 'githubName',
            is_active: true,
            manager_name: 'Test Manager',
            profile_url: 'www.test.com',
            role_name: 'Tester',
            slack_url: 'www.slack.com',
            team_name: 'QA',
          },
          getUserById: jest.fn(),
        };
        // @ts-ignore : complains about match
        subject = shallow(<ProfilePage {...props} match={{params: {userId: 'test0'}}}/>);
    });

    describe('constructor', () => {
        it('sets the userId if it exists on match.params', () => {
            expect(subject.instance().userId).toEqual('test0');
        });

        it('sets the userId as empty string if no match.params.userId', () => {
            // @ts-ignore : complains about match
            subject = shallow(<ProfilePage {...props} match={{params: {}}}/>);
            expect(subject.instance().userId).toEqual('');
        });
    });

    describe('componentDidMount', () => {
        it('calls props.getUserById', () => {
            expect(props.getUserById).toHaveBeenCalled();
        });
    });

    describe('createEmptyTabMessage', () => {
        let content;
        beforeEach(() => {
            content = subject.instance().createEmptyTabMessage('Empty message');
        });
        it('creates div w/ correct class', () => {
            expect(shallow(content).find('div').props().className).toEqual('empty-tab-message');
        });

        it('creates text with given message', () => {
            expect(shallow(content).find('text').text()).toEqual('Empty message');
        });
    });

    /* TODO: Implement proper test when the real logic for this component is written */
    describe('generateTabInfo', () => {
        let tabInfoArray;
        beforeEach(() => {
            tabInfoArray = subject.instance().generateTabInfo();
        });
        it('has a passing test so that it does not throw an error', () => {
            expect(true).toEqual(true);
        });
    });

    describe('render', () => {
        it('renders DocumentTitle w/ correct title', () => {
            expect(subject.find(DocumentTitle).props().title).toEqual(`${props.user.display_name} - Amundsen Profile`);
        });

        it('renders Breadcrumb with correct props', () => {
            expect(subject.find(Breadcrumb).props()).toMatchObject({
              path: '/',
              text: 'Search Results',
            });
        });

        it('renders Avatar for user.display_name', () => {
            /* Note: subject.find(Avatar) does not work - workaround is to directly check the content */
            const expectedContent = <Avatar name={props.user.display_name} size={74} round={true} />;
            expect(subject.find('#profile-avatar').props().children).toEqual(expectedContent);
        });

        it('does not render Avatar if user.display_name is empty string', () => {
            props.user.display_name = '';
            subject.setProps(props);
            expect(subject.find('#profile-avatar').children().exists()).toBeFalsy();
        });

        it('renders header with display_name', () => {
            expect(subject.find('#profile-title').find('h1').text()).toEqual(props.user.display_name);
        });

        it('renders Flag with correct props if user not active', () => {
            props.user.is_active = false;
            subject.setProps(props);
            expect(subject.find('#profile-title').find(Flag).props()).toMatchObject({
              caseType: 'sentenceCase',
              labelStyle: 'label-danger',
              text: 'Alumni',
            });
        });

        it('renders user role', () => {
            expect(subject.find('#user-role').text()).toEqual('Tester on QA');
        });

        it('renders user manager', () => {
            expect(subject.find('#user-manager').text()).toEqual('Manager: Test Manager');
        });

        it('renders user manager', () => {
            expect(subject.find('#user-manager').text()).toEqual('Manager: Test Manager');
        });

        it('renders slack link with correct href if user.is_active', () => {
            props.user.is_active = true;
            subject.setProps(props);
            expect(subject.find('#slack-link').props().href).toEqual('www.slack.com');
        });

        it('renders slack link with correct text if user.is_active', () => {
            props.user.is_active = true;
            subject.setProps(props);
            expect(subject.find('#slack-link').find('span').text()).toEqual('Slack');
        });

        it('renders email link with correct href if user.is_active', () => {
            props.user.is_active = true;
            subject.setProps(props);
            expect(subject.find('#email-link').props().href).toEqual('mailto:test@test.com');
        });

        it('renders email link with correct text if user.is_active', () => {
            props.user.is_active = true;
            subject.setProps(props);
            expect(subject.find('#email-link').find('span').text()).toEqual('test@test.com');
        });

        it('renders profile link with correct href if user.is_active', () => {
            props.user.is_active = true;
            subject.setProps(props);
            expect(subject.find('#profile-link').props().href).toEqual('www.test.com');
        });

        it('renders profile link with correct text if user.is_active', () => {
            props.user.is_active = true;
            subject.setProps(props);
            expect(subject.find('#profile-link').find('span').text()).toEqual('Employee Profile');
        });

        it('renders github link with correct href', () => {
            expect(subject.find('#github-link').props().href).toEqual('https://github.com/githubName');
        });

        it('renders github link with correct text', () => {
            expect(subject.find('#github-link').find('span').text()).toEqual('Github');
        });

        it('renders Tabs w/ correct props', () => {
            expect(subject.find('#profile-tabs').find(Tabs).props()).toMatchObject({
              tabs: subject.instance().generateTabInfo(),
              defaultTab: 'frequentUses_tab',
            });
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

    it('sets getUserById on the props', () => {
        expect(result.getUserById).toBeInstanceOf(Function);
    });
});

describe('mapStateToProps', () => {
    let result;
    beforeEach(() => {
        result = mapStateToProps(globalState);
    });

    it('sets user on the props', () => {
        expect(result.user).toEqual(globalState.user.profileUser);
    });
});
