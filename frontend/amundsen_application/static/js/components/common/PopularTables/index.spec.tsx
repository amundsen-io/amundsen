import * as React from 'react';
import { shallow } from 'enzyme';

import {
  POPULAR_TABLES_INFO_TEXT,
  POPULAR_TABLES_LABEL,
  POPULAR_TABLES_PER_PAGE,
  POPULAR_TABLES_SOURCE_NAME,
} from './constants';
import InfoButton from 'components/common/InfoButton';
import PaginatedResourceList from 'components/common/ResourceList/PaginatedResourceList';
import globalState from 'fixtures/globalState';
import { PopularTables, PopularTablesProps, mapStateToProps, mapDispatchToProps } from './';

describe('PopularTables', () => {
  const setup = (propOverrides?: Partial<PopularTablesProps>) => {
    const props: PopularTablesProps = {
      popularTables: jest.fn() as any,
      getPopularTables: jest.fn(),
      ...propOverrides
    };
    const wrapper = shallow<PopularTables>(<PopularTables {...props} />)

    return { props, wrapper };
  };
  let wrapper;
  let props;

  describe('componentDidMount', () => {
    let getPopularTablesSpy;
    beforeAll(() => {
      const setupResult = setup();
      wrapper = setupResult.wrapper;
      props = setupResult.props;
      getPopularTablesSpy = jest.spyOn(props, 'getPopularTables');
    });

    it('calls getPopularTables', () => {
      expect(getPopularTablesSpy).toHaveBeenCalled();
    });
  });

  describe('mapStateToProps', () => {
    let result;

    beforeAll(() => {
      result = mapStateToProps(globalState);
    });

    it('sets popularTables on the props', () => {
      expect(result.popularTables).toEqual(globalState.popularTables);
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
      const setupResult = setup();
      wrapper = setupResult.wrapper;
      props = setupResult.props;
    });
    it('renders correct label for content', () => {
      expect(wrapper.children().find('label').text()).toEqual(POPULAR_TABLES_LABEL);
    });

    it('renders InfoButton with correct props', () => {
      expect(wrapper.children().find(InfoButton).props()).toMatchObject({
        infoText: POPULAR_TABLES_INFO_TEXT,
      });
    });

    it('renders PaginatedResourceList with correct props', () => {
      expect(wrapper.children().find(PaginatedResourceList).props()).toMatchObject({
        allItems: props.popularTables,
        itemsPerPage: POPULAR_TABLES_PER_PAGE,
        source: POPULAR_TABLES_SOURCE_NAME,
      });
    });
  });
});
