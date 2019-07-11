import axios from 'axios';

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
  })
  it('getTableQueryParams',() => {
    const tableKey = 'testKey';
    expect(Helpers.getTableQueryParams(tableKey)).toEqual(`key=${encodeURIComponent(tableKey)}`)
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
