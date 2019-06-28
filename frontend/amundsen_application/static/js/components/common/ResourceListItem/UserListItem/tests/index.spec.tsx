import * as React from 'react';

import { shallow } from 'enzyme';

import * as Avatar from 'react-avatar';
import Flag from 'components/common/Flag';
import { Link } from 'react-router-dom';

import UserListItem, { UserListItemProps } from '../';
import { ResourceType } from 'interfaces';

describe('UserListItem', () => {
  const setup = (propOverrides?: Partial<UserListItemProps>) => {
    const props: UserListItemProps = {
      logging: { source: 'src', index: 0 },
      user: {
        type: ResourceType.user,
        display_name: 'firstname lastname',
        email: 'test@test.com',
        employee_type: 'fulltime',
        first_name: 'firstname',
        full_name: 'firstname lastname',
        github_username: 'githubName',
        is_active: true,
        last_name: 'lastname',
        manager_fullname: 'Test Manager',
        profile_url: 'www.test.com',
        role_name: 'Tester',
        slack_id: 'www.slack.com',
        team_name: 'QA',
        user_id: 'test0',
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
        name: props.user.display_name,
        size: 24,
        round: true,
      });
    });

    it('renders user.name', () => {
      expect(wrapper.find('.content').children().at(0).children().at(0).children().at(0).text()).toEqual(props.user.display_name);
    });

    it('does not render Alumni flag if user is active', () => {
      expect(wrapper.find('.content').children().at(0).children().at(0).find(Flag).exists()).toBeFalsy();
    });

    it('renders description', () => {
      expect(wrapper.find('.content').children().at(0).children().at(1).text()).toEqual(`${props.user.role_name} on ${props.user.team_name}`);
    });

    it('renders Alumni flag if user not active', () => {
      const wrapper = setup({
        user: {
          type: ResourceType.user,
          display_name: 'firstname lastname',
          email: 'test@test.com',
          employee_type: 'fulltime',
          first_name: 'firstname',
          full_name: 'firstname lastname',
          github_username: 'githubName',
          is_active: false,
          last_name: 'lastname',
          manager_fullname: 'Test Manager',
          profile_url: 'www.test.com',
          role_name: 'Tester',
          slack_id: 'www.slack.com',
          team_name: 'QA',
          user_id: 'test0',
        }
      }).wrapper;
      expect(wrapper.find('.content').children().at(0).children().at(0).find(Flag).exists()).toBeTruthy();
    });
  });

  describe('getLink', () => {
    it('getLink returns correct string', () => {
      const { props, wrapper } = setup();
      const { user, logging } = props;
      expect(wrapper.instance().getLink()).toEqual(`/user/${user.user_id}/?index=${logging.index}&source=${logging.source}`);
    });
  });
});
