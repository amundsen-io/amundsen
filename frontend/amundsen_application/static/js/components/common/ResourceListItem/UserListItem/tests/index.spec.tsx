import * as React from 'react';

import { shallow } from 'enzyme';

import * as Avatar from 'react-avatar';
import Flag from 'components/common/Flag';
import { Link } from 'react-router-dom';

import UserListItem, { UserListItemProps } from '../';
import { ResourceType } from '../../types';

describe('UserListItem', () => {
  const setup = (propOverrides?: Partial<UserListItemProps>) => {
    const props: UserListItemProps = {
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
      ...propOverrides
    };
    const wrapper = shallow<UserListItem>(<UserListItem {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    let props: UserListItemProps;
    let wrapper;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders item as Link', () => {
      expect(wrapper.find(Link).exists()).toBeTruthy();
    });

    it('renders Avatar', () => {
      expect(wrapper.find(Link).find(Avatar).props()).toMatchObject({
        name: props.user.name,
        size: 24,
        round: true,
      });
    });

    it('renders user.name', () => {
      expect(wrapper.find('.content').children().at(0).children().at(0).children().at(0).text()).toEqual(props.user.name);
    });

    it('does not render Alumni flag if user is active', () => {
      expect(wrapper.find('.content').children().at(0).children().at(0).find(Flag).exists()).toBeFalsy();
    });

    it('renders description', () => {
      expect(wrapper.find('.content').children().at(0).children().at(1).text()).toEqual(`${props.user.role} on ${props.user.team_name}`);
    });

    it('renders Alumni flag if user not active', () => {
      const wrapper = setup({
        user: {
          type: ResourceType.user,
          active: false,
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
        }
      }).wrapper;
      expect(wrapper.find('.content').children().at(0).children().at(0).find(Flag).exists()).toBeTruthy();
    });
  });

  describe('getLink', () => {
    it('getLink returns correct string', () => {
      const { props, wrapper } = setup();
      const { user, logging } = props;
      expect(wrapper.instance().getLink()).toEqual(`/user/${user.id}/?index=${logging.index}&source=${logging.source}`);
    });
  });
});
