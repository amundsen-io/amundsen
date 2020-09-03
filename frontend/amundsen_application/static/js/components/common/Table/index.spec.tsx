// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

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

    describe('data', () => {
      describe('when empty data is passed', () => {
        const { columns, data } = dataBuilder.withEmptyData().build();

        it('renders a table', () => {
          const { wrapper } = setup({
            data,
            columns,
          });
          const expected = 1;
          const actual = wrapper.find('.ams-table').length;

          expect(actual).toEqual(expected);
        });

        describe('table header', () => {
          it('renders a table header', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = 1;
            const actual = wrapper.find('.ams-table-header').length;

            expect(actual).toEqual(expected);
          });

          it('renders one cell inside the header', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = 1;
            const actual = wrapper.find(
              '.ams-table-header .ams-table-heading-cell'
            ).length;

            expect(actual).toEqual(expected);
          });
        });

        describe('table body', () => {
          it('renders a table body', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = 1;
            const actual = wrapper.find('.ams-table-body').length;

            expect(actual).toEqual(expected);
          });

          it('renders one row', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = 1;
            const actual = wrapper.find('.ams-table-row').length;

            expect(actual).toEqual(expected);
          });

          it('renders an empty message', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = 1;
            const actual = wrapper.find(
              '.ams-table-row .ams-empty-message-cell'
            ).length;

            expect(actual).toEqual(expected);
          });
        });
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
            const actual = wrapper.find('.ams-table-row .ams-table-cell')
              .length;

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
            const actual = wrapper.find('.ams-table-row .ams-table-cell')
              .length;

            expect(actual).toEqual(expected);
          });
        });
      });
    });

    describe('colums', () => {
      describe('when horizontal alignment is passed', () => {
        const { columns, data } = dataBuilder.withAlignedColumns().build();

        describe('table header', () => {
          it('renders the first column as left aligned', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = { textAlign: 'left' };
            const actual = wrapper
              .find('.ams-table-header .ams-table-heading-cell')
              .get(0).props.style;

            expect(actual).toEqual(expected);
          });

          it('renders the second column as center aligned', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = { textAlign: 'center' };
            const actual = wrapper
              .find('.ams-table-header .ams-table-heading-cell')
              .get(1).props.style;

            expect(actual).toEqual(expected);
          });

          it('renders the first column as right aligned', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = { textAlign: 'right' };
            const actual = wrapper
              .find('.ams-table-header .ams-table-heading-cell')
              .get(2).props.style;

            expect(actual).toEqual(expected);
          });
        });

        describe('table body', () => {
          it('renders the first column as left aligned', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = { textAlign: 'left' };
            const actual = wrapper
              .find('.ams-table-body .ams-table-cell')
              .get(0).props.style;

            expect(actual).toEqual(expected);
          });

          it('renders the second column as center aligned', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = { textAlign: 'center' };
            const actual = wrapper
              .find('.ams-table-body .ams-table-cell')
              .get(1).props.style;

            expect(actual).toEqual(expected);
          });

          it('renders the first column as right aligned', () => {
            const { wrapper } = setup({
              data,
              columns,
            });
            const expected = { textAlign: 'right' };
            const actual = wrapper
              .find('.ams-table-body .ams-table-cell')
              .get(2).props.style;

            expect(actual).toEqual(expected);
          });
        });
      });
    });

    describe('options', () => {
      describe('when a tableClassName is passed', () => {
        it('adds the class to the table', () => {
          const { wrapper } = setup({
            options: { tableClassName: 'test-class' },
          });
          const expected = 1;
          const actual = wrapper.find('.test-class').length;

          expect(actual).toEqual(expected);
        });
      });

      describe('when a rowHeight is passed', () => {
        it('adds the styling to the rows', () => {
          const { wrapper } = setup({
            options: { rowHeight: 20 },
          });
          const expected = { height: '20px' };
          const actual = wrapper.find('.ams-table-row').get(0).props.style;

          expect(actual).toEqual(expected);
        });
      });

      describe('when isLoading is active', () => {
        it('renders a table', () => {
          const { wrapper } = setup({
            data: [],
            columns: [],
            options: {
              isLoading: true,
              numLoadingBlocks: 10,
            },
          });
          const expected = 1;
          const actual = wrapper.find('.ams-table').length;

          expect(actual).toEqual(expected);
        });

        describe('table header', () => {
          it('renders a table header', () => {
            const { wrapper } = setup({
              data: [],
              columns: [],
              options: {
                isLoading: true,
              },
            });
            const expected = 1;
            const actual = wrapper.find('.ams-table-header').length;

            expect(actual).toEqual(expected);
          });

          it('renders one cell inside the header', () => {
            const { wrapper } = setup({
              data: [],
              columns: [],
              options: {
                isLoading: true,
                numLoadingBlocks: 10,
              },
            });
            const expected = 1;
            const actual = wrapper.find(
              '.ams-table-header .ams-table-heading-loading-cell'
            ).length;

            expect(actual).toEqual(expected);
          });

          it('renders one loading block inside the header', () => {
            const { wrapper } = setup({
              data: [],
              columns: [],
              options: {
                isLoading: true,
                numLoadingBlocks: 10,
              },
            });
            const expected = 1;
            const actual = wrapper.find(
              '.ams-table-header .ams-table-shimmer-block'
            ).length;

            expect(actual).toEqual(expected);
          });
        });

        describe('table body', () => {
          it('renders a table body', () => {
            const { wrapper } = setup({
              data: [],
              columns: [],
              options: {
                isLoading: true,
                numLoadingBlocks: 10,
              },
            });
            const expected = 1;
            const actual = wrapper.find('.ams-table-body').length;

            expect(actual).toEqual(expected);
          });

          it('renders one row', () => {
            const { wrapper } = setup({
              data: [],
              columns: [],
              options: {
                isLoading: true,
                numLoadingBlocks: 10,
              },
            });
            const expected = 1;
            const actual = wrapper.find('.ams-table-row').length;

            expect(actual).toEqual(expected);
          });

          it('renders the proper number of shimmering blocks', () => {
            const numOfLoadingBlocks = 10;
            const { wrapper } = setup({
              data: [],
              columns: [],
              options: {
                isLoading: true,
                numLoadingBlocks: numOfLoadingBlocks,
              },
            });
            const expected = numOfLoadingBlocks;
            const actual = wrapper.find(
              '.ams-table-row .shimmer-resource-loader-item'
            ).length;

            expect(actual).toEqual(expected);
          });
        });
      });
    });
  });

  describe('lifetime', () => {});
});
