// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { mocked } from 'ts-jest/utils';

import { GlobalState } from 'ducks/rootReducer';

import globalState from 'fixtures/globalState';

import { mapDispatchToProps, mapStateToProps } from '.';

jest.mock('config/config-utils', () => ({
  indexUsersEnabled: jest.fn(),
}));

describe('mapStateToProps', () => {
  let result;
  let expectedItemProps;
  let mockState: GlobalState;

  beforeAll(() => {
    mockState = {
      ...globalState,
      tableMetadata: {
        ...globalState.tableMetadata,
      },
    };
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;

  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets onUpdateList props to trigger desired action', () => {
    expect(result.onUpdateList).toBeInstanceOf(Function);
  });
});
