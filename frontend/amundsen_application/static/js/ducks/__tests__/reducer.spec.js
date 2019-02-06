import { createStore } from 'redux';

import rootReducer from '../reducer';
import search, { EXECUTE_SEARCH } from '../search';
import popularTables, { GET_POPULAR_TABLES } from '../popularTables';

describe('test root reducer', () => {
  let store;
  let mockResults;

  beforeEach(() => {
    mockResults = [{
      key: 'test_key',
      name: 'test_table',
      description: 'This is a test',
      database: 'test_db',
      schema_name: 'test_schema',
    }];
    store = createStore(rootReducer);
  });

  it('matches expected default state', () => {
    expect(store.getState().search.pageIndex).toEqual(search(undefined, {}).pageIndex);
    expect(store.getState().popularTables).toEqual(popularTables(undefined, {}));
    expect(store.getState().search.searchResults).toEqual(search(undefined, {}).searchResults);
    expect(store.getState().search.searchTerm).toEqual(search(undefined, {}).searchTerm);
    expect(store.getState().search.totalResults).toEqual(search(undefined, {}).totalResults);
  });

  it('verifies app state after EXECUTE_SEARCH action', () => {
    const payload = {
      data: {
        page_index: 1,
        results: mockResults,
        search_term: 'test',
        total_results: 1,
      },
    };
    const action = { type: EXECUTE_SEARCH, payload };
    store.dispatch(action);
    expect(store.getState().search.pageIndex).toEqual(1);
    expect(store.getState().popularTables).toEqual([]);
    expect(store.getState().search.searchResults).toEqual(mockResults);
    expect(store.getState().search.searchTerm).toEqual('test');
    expect(store.getState().search.totalResults).toEqual(1);
  });

  it('verified app state after GET_POPULAR_TABLES action', () => {
    const payload = {
      data: {
        results: mockResults,
      },
    };
    const action = { type: GET_POPULAR_TABLES, payload };
    store.dispatch(action);
    expect(store.getState().search.pageIndex).toEqual(0);
    expect(store.getState().popularTables).toEqual(mockResults);
    expect(store.getState().search.searchResults).toEqual([]);
    expect(store.getState().search.searchTerm).toEqual('');
    expect(store.getState().search.totalResults).toEqual(0);
  });
});
