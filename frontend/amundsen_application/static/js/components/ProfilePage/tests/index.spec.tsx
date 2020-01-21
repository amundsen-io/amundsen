import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as Avatar from 'react-avatar';

import { shallow } from 'enzyme';

import Breadcrumb from 'components/common/Breadcrumb';
import Flag from 'components/common/Flag';
import Tabs from 'components/common/Tabs';
import { mapDispatchToProps, mapStateToProps, ProfilePage, ProfilePageProps, RouteProps } from '../';

import globalState from 'fixtures/globalState';
import { getMockRouterProps } from 'fixtures/mockRouter';
import { ResourceType } from 'interfaces/Resources';

import {
  AVATAR_SIZE,
  BOOKMARKED_LABEL,
  BOOKMARKED_SOURCE,
  BOOKMARKED_TAB_KEY,
  OWNED_LABEL, OWNED_SOURCE,
  OWNED_TAB_KEY, READ_LABEL,
  READ_SOURCE, READ_TAB_KEY,
} from '../constants';

describe('ProfilePage', () => {
  const setup = (propOverrides?: Partial<ProfilePageProps>) => {
    const routerProps = getMockRouterProps<RouteProps>({userId: 'test0'}, null);
    const props: ProfilePageProps = {
      user: globalState.user.profile.user,
      bookmarks: [
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
        ],
      read: [],
      own: [],
      getUserById: jest.fn(),
      getUserOwn: jest.fn(),
      getUserRead: jest.fn(),
      getBookmarksForUser: jest.fn(),
      ...routerProps,
      ...propOverrides
    };
    const wrapper = shallow<ProfilePage>(<ProfilePage {...props} />);
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
  });

  describe('componentDidMount', () => {
    it('calls loadUserInfo', () => {
      const { props, wrapper } = setup();
      const loadUserInfoSpy = jest.spyOn(wrapper.instance(), 'loadUserInfo');
      wrapper.instance().componentDidMount();
      expect(loadUserInfoSpy).toHaveBeenCalled();
    });
  });

  describe('componentDidUpdate', () => {
    let props;
    let wrapper;
    let loadUserInfoSpy;

    beforeEach(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      loadUserInfoSpy = jest.spyOn(wrapper.instance(), 'loadUserInfo');
    });

    it('calls loadUserInfo when userId has changes', () => {
      wrapper.setProps({ match: { params: { userId: 'newUserId' }}});
      expect(loadUserInfoSpy).toHaveBeenCalled();
    });

    it('does not call loadUserInfo when userId has not changed', () => {
      wrapper.instance().componentDidUpdate();
      expect(loadUserInfoSpy).not.toHaveBeenCalled();
    });
  });


  describe('loadUserInfo', () => {
    it('calls getLoggingParams', () => {
      const { props, wrapper } = setup();
      const getLoggingParamsSpy = jest.spyOn(wrapper.instance(), 'getLoggingParams');
      wrapper.instance().loadUserInfo('test')
      expect(getLoggingParamsSpy).toHaveBeenCalledWith(props.location.search);
    });

    it('calls props.getUserById', () => {
      const { props, wrapper } = setup();
      expect(props.getUserById).toHaveBeenCalled();
    });

    it('calls props.getUserOwn', () => {
      const { props, wrapper } = setup();
      expect(props.getUserOwn).toHaveBeenCalled();
    });

    it('calls props.getUserRead', () => {
      const { props, wrapper } = setup();
      expect(props.getUserRead).toHaveBeenCalled();
    });

    it('calls props.getBookmarksForUser', () => {
      const { props, wrapper } = setup();
      expect(props.getBookmarksForUser).toHaveBeenCalled();
    });
  });

  describe('getLoggingParams', () => {
    let searchString;
    let props;
    let wrapper;
    let replaceStateSpy;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      replaceStateSpy = jest.spyOn(window.history, 'replaceState');
    });

    it('returns the parsed source and index in an object', () => {
      searchString = 'source=test_source&index=10';
      const params = wrapper.instance().getLoggingParams(searchString);
      expect(params.source).toEqual('test_source');
      expect(params.index).toEqual('10');
    });

    it('clears the logging params from the URL, if present', () => {
      searchString = 'source=test_source&index=10';
      replaceStateSpy.mockClear();
      wrapper.instance().getLoggingParams(searchString);
      expect(replaceStateSpy).toHaveBeenCalledWith({}, '', `${window.location.origin}${window.location.pathname}`);
    });

    it('does not clear the logging params if they do not exist', () => {
      searchString = '';
      replaceStateSpy.mockClear();
      wrapper.instance().getLoggingParams(searchString);
      expect(replaceStateSpy).not.toHaveBeenCalled()
    });
  });

  describe('getTabContent', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('returns an empty tab message when there are no items to render', () => {
      const content = wrapper.instance().getTabContent([], 'source', 'label');
      expect(shallow(content).find('.empty-tab-message').exists()).toBe(true)
    });

    it('renders a ResourceList with the correct props', () => {
      const content = wrapper.instance().getTabContent(props.bookmarks, 'source', 'label');
      // 'getTabContent' returns a <ResourceList> which shallow will actually render.
      // The intent here is not to test the functionality of <ResourceList>
      expect(content.props.allItems).toEqual(props.bookmarks);
      expect(content.props.source).toEqual('source');
    });
  });

  describe('generateTabInfo', () => {
    let tabInfoArray;
    let props;
    let wrapper;
    let getTabContentSpy;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
      getTabContentSpy = jest.spyOn(wrapper.instance(), 'getTabContent');
      tabInfoArray = wrapper.instance().generateTabInfo();
    });

    it('returns a tab info array with 3 tabs', () => {
      expect(tabInfoArray.length).toEqual(3);
    });

    it('tabInfo contains a tab for frequently used resources', () => {
      expect(tabInfoArray.find(tab => tab.key === READ_TAB_KEY)).toBeDefined()
    });

    it('tabInfo contains a tab for bookmarked resources', () => {
      expect(tabInfoArray.find(tab => tab.key === BOOKMARKED_TAB_KEY)).toBeDefined()
    });

    it('tabInfo contains a tab for owned resources', () => {
      expect(tabInfoArray.find(tab => tab.key === OWNED_TAB_KEY)).toBeDefined()
    });

    it ('calls getTabContent for each of 3 tabs', () => {
      expect(getTabContentSpy).toHaveBeenCalledTimes(3);
      expect(getTabContentSpy).toHaveBeenCalledWith(props.own, OWNED_SOURCE, OWNED_LABEL);
      expect(getTabContentSpy).toHaveBeenCalledWith(props.read, READ_SOURCE, READ_LABEL);
      expect(getTabContentSpy).toHaveBeenCalledWith(props.bookmarks, BOOKMARKED_SOURCE, BOOKMARKED_LABEL);
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

    it('renders Breadcrumb', () => {
      expect(wrapper.find(Breadcrumb).exists()).toBe(true)
    });

    it('renders Avatar for user.display_name', () => {
      expect(wrapper.find(Avatar).props()).toMatchObject({
        name: props.user.display_name,
        size: AVATAR_SIZE,
        round: true,
      });
    });

    it('does not render Avatar if user.display_name is empty string', () => {

      const userCopy = {
        ...globalState.user.profile.user,
        display_name: "",
      } ;
      const wrapper = setup({
        user: userCopy,
      }).wrapper;
      expect(wrapper.find('#profile-avatar').children().exists()).toBeFalsy();
    });

    it('renders header with display_name', () => {
      expect(wrapper.find('.header-title-text').text()).toContain(props.user.display_name);
    });

    it('renders Flag with correct props if user not active', () => {
      const userCopy = {
        ...globalState.user.profile.user,
        is_active: false,
      };
      const wrapper = setup({
        user: userCopy,
      }).wrapper;
      expect(wrapper.find('.header-title-text').find(Flag).props()).toMatchObject({
        caseType: 'sentenceCase',
        labelStyle: 'danger',
        text: 'Alumni',
      });
    });

    it('renders user role', () => {
      expect(wrapper.find('#user-role').text()).toEqual('Tester');
    });

    it('renders user team name', () => {
      expect(wrapper.find('#team-name').text()).toEqual('QA');
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
      expect(wrapper.find('.profile-tabs').find(Tabs).props()).toMatchObject({
        tabs: wrapper.instance().generateTabInfo(),
        defaultTab: BOOKMARKED_TAB_KEY,
      });
    });

    describe('if user.is_active', () => {
      // TODO - Uncomment when slack integration is built
      // it('renders slack link with correct href', () => {
      //   expect(wrapper.find('#slack-link').props().href).toEqual('www.slack.com');
      // });
      //
      // it('renders slack link with correct text', () => {
      //   expect(wrapper.find('#slack-link').find('span').text()).toEqual('Slack');
      // });

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

  it('sets getUserOwn on the props', () => {
    expect(result.getUserOwn).toBeInstanceOf(Function);
  });

  it('sets getUserRead on the props', () => {
    expect(result.getUserRead).toBeInstanceOf(Function);
  });

  it('sets getBookmarksForUser on the props', () => {
    expect(result.getBookmarksForUser).toBeInstanceOf(Function);
  });
});

describe('mapStateToProps', () => {
  let result;
  beforeEach(() => {
    result = mapStateToProps(globalState);
  });

  it('sets user on the props', () => {
    expect(result.user).toEqual(globalState.user.profile.user);
  });

  it('sets bookmarks on the props', () => {
    expect(result.bookmarks).toEqual(globalState.bookmarks.bookmarksForUser);
  });

  it('sets own on the props', () => {
    expect(result.own).toEqual(globalState.user.profile.own);
  });

  it('sets read on the props', () => {
    expect(result.read).toEqual(globalState.user.profile.read);
  });
});
