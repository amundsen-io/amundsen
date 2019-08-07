import axios from 'axios';
import * as qs from 'simple-query-string';

import * as Helpers from '../helpers';

import * as Utils from 'ducks/utilMethods';

import globalState from 'fixtures/globalState';

import * as API from '../v0';

const filterFromObjSpy = jest.spyOn(Utils, 'filterFromObj').mockImplementation((initialObject, rejectedKeys) => { return initialObject; });

jest.mock('axios');

describe('helpers', () => {
  let mockResponseData: API.TableDataAPI;
  let tableResponseData: API.TableData;
  beforeAll(() => {
    tableResponseData = {
      ...globalState.tableMetadata.tableData,
      owners: [{display_name: 'test', profile_url: 'test.io', email: 'test@test.com', user_id: 'test'}],
      tags: [{tag_count: 2, tag_name: 'zname'}, {tag_count: 1, tag_name: 'aname'}],
    };
    mockResponseData = {
     tableData: tableResponseData,
     msg: 'Success',
   };
  });

  describe('getTableQueryParams', () => {
    it('generates table query params with a key',() => {
      const tableKey = 'database://cluster.schema/table';
      const queryString = Helpers.getTableQueryParams(tableKey);
      const params = qs.parse(queryString);

      expect(params.key).toEqual(tableKey);
      expect(params.index).toEqual(undefined);
      expect(params.source).toEqual(undefined);
    });

    it('generates query params with logging params',() => {
      const tableKey = 'database://cluster.schema/table';
      const index = '4';
      const source = 'test-source';
      const queryString = Helpers.getTableQueryParams(tableKey, index, source);
      const params = qs.parse(queryString);

      expect(params.key).toEqual(tableKey);
      expect(params.index).toEqual(index);
      expect(params.source).toEqual(source);
    });
  });

  it('getTableDataFromResponseData',() => {
    Helpers.getTableDataFromResponseData(mockResponseData);
    expect(filterFromObjSpy).toHaveBeenCalledWith(tableResponseData, ['owners', 'tags']);
  });

  it('getTableOwnersFromResponseData',() => {
    expect(Helpers.getTableOwnersFromResponseData(mockResponseData)).toEqual({
      'test': {display_name: 'test', profile_url: 'test.io', email: 'test@test.com', user_id: 'test'}
    });
  });

  it('getTableTagsFromResponseData',() => {
    expect(Helpers.getTableTagsFromResponseData(mockResponseData)).toEqual([
      {tag_count: 1, tag_name: 'aname'},
      {tag_count: 2, tag_name: 'zname'},
    ]);
  });
});
