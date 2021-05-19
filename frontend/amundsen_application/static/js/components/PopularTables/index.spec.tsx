// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import InfoButton from 'components/InfoButton';
import PaginatedResourceList from 'components/ResourceList/PaginatedResourceList';
import globalState from 'fixtures/globalState';
import {
  POPULAR_TABLES_INFO_TEXT,
  POPULAR_TABLES_LABEL,
  POPULAR_TABLES_PER_PAGE,
  POPULAR_TABLES_SOURCE_NAME,
} from './constants';
import {
  PopularTables,
  PopularTablesProps,
  mapStateToProps,
  mapDispatchToProps,
} from '.';

const setup = (propOverrides?: Partial<PopularTablesProps>) => {
  const props: PopularTablesProps = {
    isLoaded: false,
    popularTables: jest.fn() as any,
    getPopularTables: jest.fn(),
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = shallow<PopularTables>(<PopularTables {...props} />);

  return {
    props,
    wrapper,
  };
};

describe('PopularTables', () => {
  let wrapper;
  let props;

  describe('componentDidMount', () => {
    let getPopularTablesSpy;

    beforeAll(() => {
      ({ wrapper, props } = setup());

      getPopularTablesSpy = jest.spyOn(props, 'getPopularTables');
    });

    it('calls getPopularTables', () => {
      expect(getPopularTablesSpy).toHaveBeenCalled();
    });
  });

  describe('mapStateToProps', () => {
    it('sets popularTables on the props', () => {
      const actual = mapStateToProps(globalState).popularTables;
      const expected = globalState.popularTables.popularTables;

      expect(actual).toEqual(expected);
    });
  });

  describe('mapDispatchToProps', () => {
    let result;

    beforeAll(() => {
      const dispatch = jest.fn(() => Promise.resolve());
      result = mapDispatchToProps(dispatch);
    });

    it('sets getPopularTables on the props', () => {
      expect(result.getPopularTables).toBeInstanceOf(Function);
    });
  });

  describe('render', () => {
    beforeAll(() => {
      ({ wrapper, props } = setup());
    });

    it('renders correct label for content', () => {
      const expected = POPULAR_TABLES_LABEL;
      const actual = wrapper
        .children()
        .find('.popular-tables-header-text')
        .text();

      expect(actual).toEqual(expected);
    });

    it('renders InfoButton with correct props', () => {
      expect(wrapper.children().find(InfoButton).props()).toMatchObject({
        infoText: POPULAR_TABLES_INFO_TEXT,
      });
    });

    describe('when loading', () => {
      it('renders loading state', () => {
        const actual = wrapper.find('ShimmeringResourceLoader').length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when loaded', () => {
      beforeAll(() => {
        ({ wrapper, props } = setup({
          isLoaded: true,
          popularTables: globalState.popularTables.popularTables,
        }));
      });

      it('renders PaginatedResourceList with correct props', () => {
        const actual = wrapper.children().find(PaginatedResourceList).props();
        const expected = {
          allItems: props.popularTables,
          itemsPerPage: POPULAR_TABLES_PER_PAGE,
          source: POPULAR_TABLES_SOURCE_NAME,
        };

        expect(actual).toMatchObject(expected);
      });
    });
  });
});
