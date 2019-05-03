import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as Avatar from 'react-avatar';

import { shallow } from 'enzyme';

import Breadcrumb from 'components/common/Breadcrumb';
import Flag from 'components/common/Flag';
import Tabs from 'components/common/Tabs';
import { ProfilePage, ProfilePageProps, mapDispatchToProps, mapStateToProps } from '../';

import globalState from 'fixtures/globalState';

describe('ProfilePage', () => {
  const setup = (propOverrides?: Partial<ProfilePageProps>) => {
    const props: ProfilePageProps = {
      user: globalState.user.profileUser,
      getUserById: jest.fn(),
      ...propOverrides
    };
    // @ts-ignore : complains about match
    const wrapper = shallow<ProfilePage>(<ProfilePage {...props} match={{params: {userId: 'test0'}}}/>);
    return { props, wrapper };
  };

  describe('constructor', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('sets the userId if it exists on match.params', () => {
      expect(wrapper.instance().getUserId()).toEqual('test0');
    });

    it('sets the userId as empty string if no match.params.userId', () => {
      // @ts-ignore : complains about match
      const wrapper = shallow<ProfilePage>(<ProfilePage {...props} match={{params: {}}}/>);
      expect(wrapper.instance().getUserId()).toEqual('');
    });
  });

  describe('componentDidMount', () => {
    it('calls props.getUserById', () => {
      const { props, wrapper } = setup();
      expect(props.getUserById).toHaveBeenCalled();
    });
  });

  describe('createEmptyTabMessage', () => {
    let content;
    beforeAll(() => {
      const { props, wrapper } = setup();
      content = wrapper.instance().createEmptyTabMessage('Empty message');
    });

    it('creates div w/ correct class', () => {
      expect(shallow(content).find('div').props().className).toEqual('empty-tab-message');
    });

    it('creates text with given message', () => {
      expect(shallow(content).find('label').text()).toEqual('Empty message');
    });
  });

  /* TODO: Implement proper test when the real logic for this component is written */
  describe('generateTabInfo', () => {
    let tabInfoArray;
    beforeAll(() => {
      const { props, wrapper } = setup();
      tabInfoArray = wrapper.instance().generateTabInfo();
    });

    it('has a passing test so that it does not throw an error', () => {
      expect(true).toEqual(true);
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders DocumentTitle w/ correct title', () => {
      expect(wrapper.find(DocumentTitle).props().title).toEqual(`${props.user.display_name} - Amundsen Profile`);
    });

    it('renders Breadcrumb with correct props', () => {
      expect(wrapper.find(Breadcrumb).props()).toMatchObject({
        path: '/',
        text: 'Search Results',
      });
    });

    it('renders Avatar for user.display_name', () => {
      expect(wrapper.find(Avatar).props()).toMatchObject({
        name: props.user.display_name,
        size: 74,
        round: true,
      });
    });

    it('does not render Avatar if user.display_name is empty string', () => {

      const userCopy = {
        ...globalState.user.profileUser,
        display_name: "",
      } ;
      const wrapper = setup({
        user: userCopy,
      }).wrapper;
      expect(wrapper.find('#profile-avatar').children().exists()).toBeFalsy();
    });

    it('renders header with display_name', () => {
      expect(wrapper.find('#profile-title').find('h1').text()).toEqual(props.user.display_name);
    });

    it('renders Flag with correct props if user not active', () => {
      const userCopy = {
        ...globalState.user.profileUser,
        is_active: false,
      };
      const wrapper = setup({
        user: userCopy,
      }).wrapper;
      expect(wrapper.find('#profile-title').find(Flag).props()).toMatchObject({
        caseType: 'sentenceCase',
        labelStyle: 'label-danger',
        text: 'Alumni',
      });
    });

    it('renders user role', () => {
      expect(wrapper.find('#user-role').text()).toEqual('Tester on QA');
    });

    it('renders user manager', () => {
      expect(wrapper.find('#user-manager').text()).toEqual('Manager: Test Manager');
    });

    it('renders user manager', () => {
      expect(wrapper.find('#user-manager').text()).toEqual('Manager: Test Manager');
    });

    it('renders github link with correct href', () => {
      expect(wrapper.find('#github-link').props().href).toEqual('https://github.com/githubName');
    });

    it('renders github link with correct text', () => {
      expect(wrapper.find('#github-link').find('span').text()).toEqual('Github');
    });

    it('renders Tabs w/ correct props', () => {
      expect(wrapper.find('#profile-tabs').find(Tabs).props()).toMatchObject({
        tabs: wrapper.instance().generateTabInfo(),
        defaultTab: 'frequentUses_tab',
      });
    });

    describe('if user.is_active', () => {
      it('renders slack link with correct href', () => {
        expect(wrapper.find('#slack-link').props().href).toEqual('www.slack.com');
      });

      it('renders slack link with correct text', () => {
        expect(wrapper.find('#slack-link').find('span').text()).toEqual('Slack');
      });

      it('renders email link with correct href', () => {
        expect(wrapper.find('#email-link').props().href).toEqual('mailto:test@test.com');
      });

      it('renders email link with correct text', () => {
        expect(wrapper.find('#email-link').find('span').text()).toEqual('test@test.com');
      });

      it('renders profile link with correct href', () => {
        expect(wrapper.find('#profile-link').props().href).toEqual('www.test.com');
      });

      it('renders profile link with correct text', () => {
        expect(wrapper.find('#profile-link').find('span').text()).toEqual('Employee Profile');
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
