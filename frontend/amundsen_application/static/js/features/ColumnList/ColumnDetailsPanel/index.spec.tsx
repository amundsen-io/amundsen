// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';
import { getColumnLink } from 'utils/navigationUtils';
import ExpandableUniqueValues from 'features/ExpandableUniqueValues';
import BadgeList from 'features/BadgeList';
import RequestDescriptionText from 'pages/TableDetailPage/RequestDescriptionText';
import ColumnDescEditableText from '../ColumnDescEditableText';
import ColumnStats from '../ColumnStats';
import ColumnLineage from '../ColumnLineage';
import ColumnType from '../ColumnType';
import ColumnDetailsPanel, { ColumnDetailsPanelProps } from '.';

const mockColumnDetails = {
  content: {
    title: 'column_name',
    description: 'description',
    nestedLevel: 0,
    hasStats: true,
  },
  type: { name: 'column_name', database: 'database', type: 'string' },
  usage: 0,
  stats: [
    {
      end_epoch: 1600473600,
      start_epoch: 1597881600,
      stat_type: 'column_usage',
      stat_val: '111',
    },
  ],
  children: [],
  action: { name: 'column_name', isActionEnabled: true },
  editText: 'Click to edit description in the data source site',
  editUrl: 'https://test.datasource.site/table',
  index: 0,
  key: 'database://cluster.schema/table/column_name',
  name: 'column_name',
  tableParams: {
    database: 'database',
    cluster: 'cluster',
    schema: 'schema',
    table: 'table',
  },
  sort_order: 0,
  isEditable: true,
  isExpandable: false,
  badges: [
    {
      badge_name: 'Badge Name 1',
      category: 'column',
    },
  ],
  typeMetadata: {
    kind: 'scalar',
    name: 'column_name',
    key: 'database://cluster.schema/table/column_name/type/column_name',
    description: 'description',
    data_type: 'string',
    sort_order: 0,
    is_editable: true,
  },
};

Object.defineProperty(navigator, 'clipboard', {
  value: { writeText: jest.fn() },
});
let mockStats = mockColumnDetails.stats;
jest.mock('utils/stats', () => ({
  filterOutUniqueValues: () => mockStats,
  getUniqueValues: () => mockStats,
}));
let mockLineageEnabled = true;
let mockNotificationsEnabled = false;
jest.mock('config/config-utils', () => ({
  isColumnListLineageEnabled: () => mockLineageEnabled,
  getMaxLength: jest.fn(),
  notificationsEnabled: () => mockNotificationsEnabled,
}));

describe('ColumnDetailsPanel', () => {
  const setup = (propOverrides?: Partial<ColumnDetailsPanelProps>) => {
    const props: ColumnDetailsPanelProps = {
      columnDetails: mockColumnDetails,
      togglePanel: jest.fn(),
      ...propOverrides,
    };
    const wrapper = shallow(<ColumnDetailsPanel {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    describe('when the details panel is open', () => {
      it('renders two copy column info buttons', () => {
        const { wrapper } = setup();

        const actual = wrapper.find('.btn-default').length;
        const expected = 2;

        expect(actual).toEqual(expected);
      });

      it('renders the column type', () => {
        const { wrapper } = setup();

        const actual = wrapper.find(ColumnType).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when badges are passed', () => {
      it('should render badges', () => {
        const { wrapper } = setup();

        const actual = wrapper.find(BadgeList).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when no badges are passed', () => {
      it('should not render badges', () => {
        const noBadgesColDetails = {
          ...mockColumnDetails,
          badges: [],
        };
        const { wrapper } = setup({ columnDetails: noBadgesColDetails });

        const actual = wrapper.find(BadgeList).length;
        const expected = 0;

        expect(actual).toEqual(expected);
      });
    });

    describe('when a description, editText, and editUrl is passed and isEditable is true', () => {
      it('should render a description', () => {
        const { wrapper } = setup();

        const actual = wrapper.find(ColumnDescEditableText).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when only the content description is set', () => {
      it('should still render a description', () => {
        const withDescriptionColDetails = {
          ...mockColumnDetails,
          content: {
            title: 'column_name',
            description: 'description',
            nestedLevel: 0,
            hasStats: true,
          },
          editText: '',
          editUrl: '',
          isEditable: false,
        };
        const { wrapper } = setup({
          columnDetails: withDescriptionColDetails,
        });

        const actual = wrapper.find(ColumnDescEditableText).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when no description, editText, or editUrl is passed and isEditable is false', () => {
      it('should not render a description', () => {
        const noDescriptionColDetails = {
          ...mockColumnDetails,
          content: {
            title: 'column_name',
            description: '',
            nestedLevel: 0,
            hasStats: true,
          },
          editText: '',
          editUrl: '',
          isEditable: false,
        };
        const { wrapper } = setup({ columnDetails: noDescriptionColDetails });

        const actual = wrapper.find(ColumnDescEditableText).length;
        const expected = 0;

        expect(actual).toEqual(expected);
      });
    });

    describe('when notifications are not enabled', () => {
      it('should not render the request description text', () => {
        mockNotificationsEnabled = false;
        const { wrapper } = setup();

        const actual = wrapper.find(RequestDescriptionText).length;
        const expected = 0;

        expect(actual).toEqual(expected);
      });
    });

    describe('when notifications are enabled', () => {
      it('should render the request description text', () => {
        mockNotificationsEnabled = true;
        const { wrapper } = setup();

        const actual = wrapper.find(RequestDescriptionText).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when column stats are passed', () => {
      it('should render stats', () => {
        mockStats = mockColumnDetails.stats;
        const { wrapper } = setup();

        const actual = wrapper.find(ColumnStats).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when column stats are not passed', () => {
      it('should not render stats', () => {
        mockStats = [];
        const noStatsColDetails = {
          ...mockColumnDetails,
          stats: [],
        };
        const { wrapper } = setup({ columnDetails: noStatsColDetails });

        const actual = wrapper.find(ColumnStats).length;
        const expected = 0;

        expect(actual).toEqual(expected);
      });
    });

    describe('when unique values are passed', () => {
      it('should render unique values', () => {
        mockStats = mockColumnDetails.stats;
        const { wrapper } = setup();

        const actual = wrapper.find(ExpandableUniqueValues).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when unique values are not passed', () => {
      it('should not render unique values', () => {
        mockStats = [];
        const noStatsColDetails = {
          ...mockColumnDetails,
          stats: [],
        };
        const { wrapper } = setup({ columnDetails: noStatsColDetails });

        const actual = wrapper.find(ExpandableUniqueValues).length;
        const expected = 0;

        expect(actual).toEqual(expected);
      });
    });

    describe('when column lineage is enabled', () => {
      it('should render lineage', () => {
        mockLineageEnabled = true;
        const { wrapper } = setup();

        const actual = wrapper.find(ColumnLineage).length;
        const expected = 1;

        expect(actual).toEqual(expected);
      });
    });

    describe('when column lineage is not enabled', () => {
      it('should not render lineage', () => {
        mockLineageEnabled = false;
        const { wrapper } = setup();

        const actual = wrapper.find(ColumnLineage).length;
        const expected = 0;

        expect(actual).toEqual(expected);
      });
    });
  });

  describe('lifecycle', () => {
    describe('when the X button is clicked', () => {
      it('triggers the panel toggle', () => {
        const { props, wrapper } = setup();

        wrapper.find('.btn-close').simulate('click');

        expect(props.togglePanel).toHaveBeenCalled();
      });
    });

    describe('when the copy column info buttons are clicked', () => {
      it('the first button copies column name', () => {
        const { wrapper } = setup();

        wrapper.find('.btn-default').first().simulate('click');

        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
          'column_name'
        );
      });

      it('the second button copies column link', () => {
        const { props, wrapper } = setup();

        wrapper.find('.btn-default').at(1).simulate('click');
        const expected = getColumnLink(
          props.columnDetails.tableParams,
          props.columnDetails.name
        );

        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(expected);
      });
    });
  });
});
