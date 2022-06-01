// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { GlobalState } from 'ducks/rootReducer';

import globalState from 'fixtures/globalState';
import { ContainerOwnProps, mapDispatchToProps, mapStateToProps } from '.';

describe('mapStateToProps', () => {
  let result;
  let expectedItemProps;
  let mockState: GlobalState;
  let mockProps: ContainerOwnProps;
  beforeAll(() => {
    mockState = {
      ...globalState,
      tableMetadata: {
        ...globalState.tableMetadata,
        tableData: {
          ...globalState.tableMetadata.tableData,
          key: 'database://cluster.schema/table',
          columns: [
            {
              badges: [],
              col_type: 'struct<col1:string,col2:int>',
              description: 'column description',
              is_editable: true,
              key: 'database://cluster.schema/table/column',
              name: 'column',
              type_metadata: {
                kind: 'struct',
                name: 'column',
                key: 'database://cluster.schema/table/column/type/column',
                description: 'type metadata description',
                data_type: 'struct<col1:string,col2:int>',
                sort_order: 0,
                is_editable: true,
              },
              sort_order: 0,
              stats: [],
            },
          ],
        },
      },
    };
  });

  it('returns expected props for a column', () => {
    mockProps = {
      columnKey: 'database://cluster.schema/table/column',
      isNestedColumn: false,
    };
    result = mapStateToProps(mockState, mockProps);
    expectedItemProps =
      mockState.tableMetadata.tableData.columns[0].description;
    expect(result.refreshValue).toEqual(expectedItemProps);
  });

  it('returns expected props for a nested column', () => {
    mockProps = {
      columnKey: 'database://cluster.schema/table/column/type/column',
      isNestedColumn: true,
    };
    result = mapStateToProps(mockState, mockProps);
    expectedItemProps =
      mockState.tableMetadata.tableData.columns[0].type_metadata?.description;
    expect(result.refreshValue).toEqual(expectedItemProps);
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  let mockProps: ContainerOwnProps;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
  });

  it('sets getLatestValue props to trigger desired action', () => {
    mockProps = {
      columnKey: 'database://cluster.schema/table/column',
      isNestedColumn: false,
    };
    result = mapDispatchToProps(dispatch, mockProps);
    expect(result.getLatestValue).toBeInstanceOf(Function);
  });
  it('sets onSubmitValue props to trigger desired action', () => {
    mockProps = {
      columnKey: 'database://cluster.schema/table/column/type/column',
      isNestedColumn: true,
    };
    result = mapDispatchToProps(dispatch, mockProps);
    expect(result.onSubmitValue).toBeInstanceOf(Function);
  });
});
