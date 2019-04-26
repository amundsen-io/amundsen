import * as React from 'react';

import { shallow } from 'enzyme';

import Avatar from 'react-avatar';
import Flag from 'components/common/Flag';
import { Link } from 'react-router-dom';

import UserListItem, { UserListItemProps } from '../';
import { ResourceType } from '../../types';

describe('UserListItem', () => {
    let props: UserListItemProps;
    let subject;

    beforeEach(() => {
        props = {
          logging: { source: 'src', index: 0 },
          user: {
            type: ResourceType.user,
            active: true,
            birthday: null,
            department: 'Department',
            email: 'test@test.com',
            first_name: '',
            github_username: '',
            id: 0,
            last_name: '',
            manager_email: '',
            name: 'Test Tester',
            offboarded: true,
            office: '',
            role: '',
            start_date: '',
            team_name: '',
            title: '',
          },
        }
        subject = shallow(<UserListItem {...props} />);
    });

    describe('render', () => {
        it('renders item as Link', () => {
          expect(subject.find(Link).exists()).toBeTruthy();
        });

        /* TODO (ttannis): Avatar tests wont pass
        it('renders Avatar', () => {
          expect(subject.find(Link).find(Avatar).exists()).toBeTruthy();
        });*/

        it('renders user.name', () => {
          expect(subject.find('.content').children().at(0).children().at(0).children().at(0).text()).toEqual(props.user.name);
        });

        it('renders Alumni flag if user not active', () => {
          props.user.active = false;
          subject.setProps(props);
          expect(subject.find('.content').children().at(0).children().at(0).find(Flag).exists()).toBeTruthy();
        });

        it('renders description', () => {
          const { user } = props;
          expect(subject.find('.content').children().at(0).children().at(1).text()).toEqual(`${user.role} on ${user.team_name}`);
        });
    });

    describe('getLink', () => {
        it('getLink returns correct string', () => {
          const { user, logging } = props;
          expect(subject.instance().getLink()).toEqual(`/user/${user.id}/?index=${logging.index}&source=${logging.source}`);
        });
    });
});
