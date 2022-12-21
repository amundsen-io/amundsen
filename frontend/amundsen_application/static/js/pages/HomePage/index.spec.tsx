// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import Breadcrumb from 'features/Breadcrumb';
import MyBookmarks from 'features/MyBookmarks';
import PopularTables from 'features/PopularResources';
import SearchBar from 'features/SearchBar';
import TagsListContainer from 'features/Tags';

import { getMockRouterProps } from 'fixtures/mockRouter';
import SearchBarWidget from 'features/HomePageWidgets/SearchBarWidget';
import {
  mapDispatchToProps,
  HomePage,
  HomePageProps,
  HomePageWidgets,
} from '.';

describe('HomePage', () => {
  const setup = (propOverrides?: Partial<HomePageProps>) => {
    const mockLocation = {
      search: '/search?searchTerm=testName&resource=table&pageIndex=1',
    };
    const routerProps = getMockRouterProps<any>(null, mockLocation);
    const props: HomePageProps = {
      searchReset: jest.fn(),
      ...routerProps,
      ...propOverrides,
    };
    const wrapper = shallow<HomePage>(<HomePage {...props} />);

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

    it('contains HomePageWidgets', () => {
      expect(wrapper.contains(<HomePageWidgets />));
    });

    it('contains a SearchBarWidget', () => {
      expect(wrapper.contains(<SearchBarWidget />));
    });

    it('contains a Breadcrumb', () => {
      expect(wrapper.contains(<Breadcrumb />));
    });

    it('contains TagsList', () => {
      expect(wrapper.contains(<TagsListContainer shortTagsList />));
    });

    it('contains MyBookmarks', () => {
      expect(wrapper.contains(<MyBookmarks />));
    });

    it('contains PopularResources', () => {
      expect(wrapper.contains(<PopularTables />));
    });
  });

  describe('componentDidMount', () => {
    it('calls searchReset', () => {
      const searchResetSpy = jest.spyOn(props, 'searchReset');

      wrapper.instance().componentDidMount();

      expect(searchResetSpy).toHaveBeenCalled();
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
