import * as React from 'react';
import { mount } from 'enzyme';

import Table, { TableProps } from '.';

import TestDataBuilder from './testDataBuilder';

const dataBuilder = new TestDataBuilder();

const setup = (propOverrides?: Partial<TableProps>) => {
  const { data, columns } = dataBuilder.build();
  const props = {
    data,
    columns,
    ...propOverrides,
  };
  const wrapper = mount<TableProps>(<Table {...props} />);

  return { props, wrapper };
};

describe('Table', () => {
  describe('render', () => {
    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    describe('when simple data is passed', () => {
      it('renders a table', () => {
        const { wrapper } = setup();
        const expected = 1;
        const actual = wrapper.find('.ams-table').length;

        expect(actual).toEqual(expected);
      });

      describe('table header', () => {
        it('renders a table header', () => {
          const { wrapper } = setup();
          const expected = 1;
          const actual = wrapper.find('.ams-table-header').length;

          expect(actual).toEqual(expected);
        });

        it('renders a three cells inside the header', () => {
          const { wrapper } = setup();
          const expected = 3;
          const actual = wrapper.find(
            '.ams-table-header .ams-table-heading-cell'
          ).length;

          expect(actual).toEqual(expected);
        });
      });

      describe('table body', () => {
        it('renders a table body', () => {
          const { wrapper } = setup();
          const expected = 1;
          const actual = wrapper.find('.ams-table-body').length;

          expect(actual).toEqual(expected);
        });

        it('renders three rows', () => {
          const { wrapper } = setup();
          const expected = 3;
          const actual = wrapper.find('.ams-table-row').length;

          expect(actual).toEqual(expected);
        });

        it('renders nine cells', () => {
          const { wrapper } = setup();
          const expected = 9;
          const actual = wrapper.find('.ams-table-row .ams-table-cell').length;

          expect(actual).toEqual(expected);
        });
      });
    });

    describe('when more data than columns', () => {
      const { columns, data } = dataBuilder.withMoreDataThanColumns().build();

      describe('table header', () => {
        it('renders a three cells inside the header', () => {
          const { wrapper } = setup({ columns, data });
          const expected = 3;
          const actual = wrapper.find(
            '.ams-table-header .ams-table-heading-cell'
          ).length;

          expect(actual).toEqual(expected);
        });
      });

      describe('table body', () => {
        it('renders four rows', () => {
          const { wrapper } = setup({ columns, data });
          const expected = 4;
          const actual = wrapper.find('.ams-table-row').length;

          expect(actual).toEqual(expected);
        });

        it('renders twelve cells', () => {
          const { wrapper } = setup({ columns, data });
          const expected = 12;
          const actual = wrapper.find('.ams-table-row .ams-table-cell').length;

          expect(actual).toEqual(expected);
        });
      });
    });
  });

  describe('lifetime', () => {});
});
