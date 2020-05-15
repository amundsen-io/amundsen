import * as React from 'react';

import { shallow } from 'enzyme';

import { mapDispatchToProps, HomePage, HomePageProps } from '.';

import Breadcrumb from 'components/common/Breadcrumb';
import MyBookmarks from 'components/common/Bookmark/MyBookmarks';
import PopularTables from 'components/common/PopularTables';
import SearchBar from 'components/common/SearchBar';
import TagsList from 'components/common/TagsList';

import { getMockRouterProps } from 'fixtures/mockRouter';

describe('HomePage', () => {
  const setup = (propOverrides?: Partial<HomePageProps>) => {
    const mockLocation = {
      search: '/search?searchTerm=testName&resource=table&pageIndex=1',
    };
    const routerProps = getMockRouterProps<any>(null, mockLocation);
    const props: HomePageProps = {
      searchReset: jest.fn(),
      ...routerProps,
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
    it('contains Searchbar', () => {
      expect(wrapper.contains(<SearchBar />));
    });

    it('contains a Breadcrumb that directs to the /search', () => {
      const element = wrapper.find(Breadcrumb);
      expect(element.exists()).toBe(true);
      expect(element.props().path).toEqual('/search');
    });

    it('contains TagsList', () => {
      expect(wrapper.find('#browse-tags-header').text()).toEqual('Browse Tags');
      expect(wrapper.contains(<TagsList />));
    });

    it('contains MyBookmarks', () => {
      expect(wrapper.contains(<MyBookmarks />));
    });

    it('contains PopularTables', () => {
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
