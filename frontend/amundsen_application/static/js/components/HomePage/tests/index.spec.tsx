import * as React from 'react';

import { shallow } from 'enzyme';

import { mapDispatchToProps, HomePage, HomePageProps } from '../';

import SearchBar from 'components/SearchPage/SearchBar';
import MyBookmarks from 'components/common/Bookmark/MyBookmarks';
import PopularTables from 'components/common/PopularTables';

describe('HomePage', () => {
  const setup = (propOverrides?: Partial<HomePageProps>) => {
    const props: HomePageProps = {
      searchReset: jest.fn(),
      history: {
        length: 2,
        action: "POP",
        location: jest.fn() as any,
        push: jest.fn(),
        replace: jest.fn(),
        go: jest.fn(),
        goBack: jest.fn(),
        goForward: jest.fn(),
        block: jest.fn(),
        createHref: jest.fn(),
        listen: jest.fn(),
      },
      location: {
        search: '/search?searchTerm=testName&selectedTab=table&pageIndex=1', 
        pathname: 'mockstr',
        state: jest.fn(),
        hash: 'mockstr',
      },
      match: jest.fn() as any,
      staticContext: jest.fn() as any,
      ...propOverrides
    };
    const wrapper = shallow<HomePage>(<HomePage {...props} />)
    return { props, wrapper };
  };
  let props;
  let wrapper;
  beforeAll(() => {
    const setupResult = setup();
    props = setupResult.props;
    wrapper = setupResult.wrapper;
  });

  describe('render', () => {
    it('contains Searchbar, BookmarkList, and PopularTables', () => {
      expect(wrapper.contains(<SearchBar />));
      expect(wrapper.contains(<MyBookmarks />));
      expect(wrapper.contains(<PopularTables />));
    });
  });
  
  describe('componentDidMount', () => {
    it('calls searchReset', () => {
      const searchResetSpy = jest.spyOn(props, 'searchReset');
      wrapper.instance().componentDidMount();
      expect(searchResetSpy).toHaveBeenCalled;
    });
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets searchReset on the props', () => {
    expect(result.searchReset).toBeInstanceOf(Function);
  });
});
