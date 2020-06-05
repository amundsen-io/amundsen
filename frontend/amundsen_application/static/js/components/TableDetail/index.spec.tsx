import * as React from 'react';
import * as History from 'history';
import { mount } from 'enzyme';

import { getMockRouterProps } from '../../fixtures/mockRouter';
import { tableMetadata } from '../../fixtures/metadata/table';

import LoadingSpinner from '../common/LoadingSpinner';

import { TableDetail, TableDetailProps, MatchProps } from './';


const setup = (propOverrides?: Partial<TableDetailProps>, location?: Partial<History.Location>) => {
  const routerProps = getMockRouterProps<MatchProps>({
    "cluster":"gold",
    "database":"hive",
    "schema":"base",
    "table":"rides"
  }, location);
  const props = {
    isLoading: false,
    statusCode: 200,
    tableData: tableMetadata,
    getTableData: jest.fn(),
    ...routerProps,
    ...propOverrides,
  };
  const wrapper = mount<TableDetail>(<TableDetail {...props} />);

  return { props, wrapper };
};

describe('TableDetail', () => {

  describe('render', () => {

      it('should render without problems', () => {
        expect(() => {setup();}).not.toThrow();
      });

      it('should render the Loading Spinner', () => {
        const {wrapper} = setup();
        const expected = 1;
        const actual = wrapper.find(LoadingSpinner).length;

        expect(actual).toEqual(expected);
      });
  });

  describe('lifecycle', () => {
    describe('when mounted', () => {
      it('calls loadDashboard with uri from state', () => {
        const { props } = setup();
        const expected = 1;
        const actual = (props.getTableData as jest.Mock).mock.calls.length;

        expect(actual).toEqual(expected);
      });
    });
  });
});
