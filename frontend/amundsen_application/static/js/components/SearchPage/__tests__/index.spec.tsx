import * as React from 'react';
import * as Adapter from 'enzyme-adapter-react-16';

import { configure, mount, shallow } from 'enzyme';

configure({ adapter: new Adapter() });

import SearchPage from '../../SearchPage';

describe('SearchPage', () => {
  const executeSearch = jest.fn();
  const testResults = [
    {
      database: "test_db",
      description: "This is the description.",
      key: "test_key",
      last_updated: 1527283287,
      name: "test_table",
      schema_name: "test_schema",
      cluster: "gold"
    },
    {
      database: "test_db2",
      description: "This is the description.",
      key: "test_key2",
      last_updated: 1527283287,
      name: "test_table2",
      schema_name: "test_schema2",
      cluster: "gold"
    }
  ];
  let testProps;

  beforeEach(() => {
    testProps = {
      executeSearch,
      getPopularTables: jest.fn(),
      searchResults: [],
      searchTerm: '',
      pageIndex: 0,
      popularTables: [],
      totalResults: 0,
    };
  });

  it('renders search results correctly', () => {
    testProps['searchResults'] = testResults;
    testProps['totalResults'] = 2;
    testProps['searchTerm'] = 'test';
    const wrapper = shallow<SearchPage>(<SearchPage {...testProps} />);
    // @ts-ignore
    expect(wrapper).toMatchSnapshot();
  });

  it('renders popular tables correctly', () => {
    testProps['popularTables'] = testResults;
    const wrapper = shallow<SearchPage>(<SearchPage {...testProps} />);
    // @ts-ignore
    expect(wrapper).toMatchSnapshot();
  });

  it('renders no results message', () => {
    testProps['searchTerm'] = 'thisisnotarealsearch';
    const wrapper = shallow<SearchPage>(<SearchPage {...testProps} />);
    // @ts-ignore
    expect(wrapper).toMatchSnapshot();
  });

  it('renders pageindex out of bounds message', () => {
    testProps['searchResults'] = testResults;
    testProps['totalResults'] = 2;
    testProps['pageIndex'] = 50;
    const wrapper = shallow<SearchPage>(<SearchPage {...testProps} />);
    // @ts-ignore
    expect(wrapper).toMatchSnapshot();
  });

  it('executes page change', () => {
    testProps['searchTerm'] = 'test';
    const wrapper = mount<SearchPage>(<SearchPage {...testProps} />);
    wrapper.instance().handlePageChange(2);
    expect(executeSearch).toHaveBeenCalledWith('test', 1);
  });
});
