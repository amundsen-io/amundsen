// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';

const defaultData = [
  {
    name: 'rowName',
    type: 'rowType',
    value: 1,
    key: 'database://cluster.schema/table/rowName',
  },
  {
    name: 'rowName2',
    type: 'rowType2',
    value: 2,
    key: 'database://cluster.schema/table/rowName2',
  },
  {
    name: 'rowName3',
    type: 'rowType3',
    value: 3,
    key: 'database://cluster.schema/table/rowName3',
  },
];

const defaultColumns = [
  {
    title: 'Name',
    field: 'name',
  },
  {
    title: 'Type',
    field: 'type',
  },
  {
    title: 'Value',
    field: 'value',
  },
];

const initalConfig = {
  data: defaultData,
  columns: defaultColumns,
};

/**
 * Generates test data for the table data
 * @example
 * let testData = new TestDataBuilder()
 *                         .withUsageRow()
 *                         .build();
 */
function TestDataBuilder(config = {}) {
  this.Klass = TestDataBuilder;
  this.config = {
    ...initalConfig,
    ...config,
  };

  this.withWrongData = () => {
    const attr = {
      data: [
        {
          name: 'rowName',
          type: 'rowType',
          value: 1,
          key: 'database://cluster.schema/table/rowName',
        },
        {
          name: 'rowName2',
          type: 'rowType2',
          value: 2,
          key: 'database://cluster.schema/table/rowName2',
        },
        {
          name: 'rowName3',
          type: 'rowType3',
          value: 3,
          key: 'database://cluster.schema/table/rowName3',
        },
      ],
      columns: [
        {
          title: 'Name',
          field: 'name',
        },
        {
          title: 'Type',
          field: 'type',
        },
        {
          title: 'Value',
          field: 'value',
        },
        {
          title: 'Bad Field',
          field: 'badfield',
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withUsageRow = () => {
    const attr = {
      data: [
        ...this.config.data,
        {
          name: 'usageRow',
          type: 'usageRowType',
          value: 4,
          key: 'database://cluster.schema/table/usageRow',
          usage: 44,
        },
      ],
      columns: [...this.config.columns, { title: 'Usage', field: 'usage' }],
    };

    return new this.Klass(attr);
  };

  this.withCollapsedRow = () => {
    const attr = {
      data: [
        {
          name: 'rowName',
          type: 'rowType',
          value: 1,
          key: 'database://cluster.schema/table/rowName',
          isExpandable: true,
          typeMetadata: {
            kind: 'array',
            name: 'rowName',
            key: 'database://cluster.schema/table/rowName/type/rowName',
            isExpandable: true,
            description: 'description',
            data_type: 'array<struct<col1:array<int>,col2:map<string,string>>>',
            sort_order: 0,
            children: [
              {
                kind: 'struct',
                name: '_inner_',
                key:
                  'database://cluster.schema/table/rowName/type/rowName/_inner_',
                isExpandable: true,
                description: 'description',
                data_type: 'struct<col1:array<int>,col2:map<string,string>>',
                sort_order: 0,
                children: [
                  {
                    kind: 'array',
                    name: 'col1',
                    key:
                      'database://cluster.schema/table/rowName/type/rowName/_inner_/col1',
                    isExpandable: false,
                    description: 'description',
                    data_type: 'array<int>',
                    sort_order: 0,
                  },
                  {
                    kind: 'map',
                    name: 'col2',
                    key:
                      'database://cluster.schema/table/rowName/type/rowName/_inner_/col2',
                    isExpandable: true,
                    description: 'description',
                    data_type: 'map<string,string>',
                    sort_order: 1,
                    children: [
                      {
                        kind: 'scalar',
                        name: '_map_key',
                        key:
                          'database://cluster.schema/table/rowName/type/rowName/_inner_/col2/_map_key',
                        isExpandable: false,
                        description: 'description',
                        data_type: 'string',
                        sort_order: 0,
                      },
                      {
                        kind: 'scalar',
                        name: '_map_value',
                        key:
                          'database://cluster.schema/table/rowName/type/rowName/_inner_/col2/_map_value',
                        isExpandable: false,
                        description: 'description',
                        data_type: 'string',
                        sort_order: 1,
                      },
                    ],
                  },
                ],
              },
            ],
          },
        },
        {
          name: 'rowName2',
          type: 'rowType2',
          value: 2,
          key: 'database://cluster.schema/table/rowName2',
          isExpandable: true,
          typeMetadata: {
            kind: 'struct',
            name: 'rowName2',
            key: 'database://cluster.schema/table/rowName2/type/rowName2',
            isExpandable: true,
            description: 'description',
            data_type: 'struct<col3:int,col4:array<map<string,string>>>',
            sort_order: 0,
            children: [
              {
                kind: 'scalar',
                name: 'col3',
                key:
                  'database://cluster.schema/table/rowName2/type/rowName2/col3',
                isExpandable: false,
                description: 'description',
                data_type: 'int',
                sort_order: 0,
              },
              {
                kind: 'array',
                name: 'col4',
                key:
                  'database://cluster.schema/table/rowName2/type/rowName2/col4',
                isExpandable: true,
                description: 'description',
                data_type: 'array<map<string,string>>',
                sort_order: 1,
                children: [
                  {
                    kind: 'map',
                    name: '_inner_',
                    key:
                      'database://cluster.schema/table/rowName2/type/rowName2/col4/_inner_',
                    isExpandable: true,
                    description: 'description',
                    data_type: 'map<string,string>',
                    sort_order: 0,
                    children: [
                      {
                        kind: 'scalar',
                        name: '_map_key',
                        key:
                          'database://cluster.schema/table/rowName2/type/rowName2/col4/_inner_/_map_key',
                        isExpandable: false,
                        description: 'description',
                        data_type: 'string',
                        sort_order: 0,
                      },
                      {
                        kind: 'scalar',
                        name: '_map_value',
                        key:
                          'database://cluster.schema/table/rowName2/type/rowName2/col4/_inner_/_map_value',
                        isExpandable: false,
                        description: 'description',
                        data_type: 'string',
                        sort_order: 1,
                      },
                    ],
                  },
                ],
              },
            ],
          },
        },
        {
          name: 'rowName3',
          type: 'rowType3',
          value: 3,
          key: 'database://cluster.schema/table/rowName3',
          isExpandable: false,
          typeMetadata: {
            kind: 'scalar',
            name: 'rowName3',
            key: 'database://cluster.schema/table/rowName3/type/rowName3',
            description: 'description',
            data_type: 'string',
            sort_order: 0,
          },
        },
      ],
      columns: [
        {
          title: 'Name',
          field: 'name',
        },
        {
          title: 'Type',
          field: 'type',
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withOneComponentColumn = () => {
    const attr = {
      data: [...this.config.data],
      columns: [
        {
          title: 'Name',
          field: 'name',
          component: (name) => <strong>{name}</strong>,
        },
        {
          title: 'Type',
          field: 'type',
        },
        {
          title: 'Value',
          field: 'value',
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withActionCell = () => {
    const attr = {
      data: [
        {
          name: 'rowName',
          type: 'rowType',
          value: 'Action Text',
          key: 'database://cluster.schema/table/rowName',
        },
        {
          name: 'rowName2',
          type: 'rowType2',
          value: 'Action Text',
          key: 'database://cluster.schema/table/rowName2',
        },
        {
          name: 'rowName3',
          type: 'rowType3',
          value: 'Action Text',
          key: 'database://cluster.schema/table/rowName3',
        },
      ],
      columns: [
        {
          title: 'Name',
          field: 'name',
        },
        {
          title: 'Type',
          field: 'type',
        },
        {
          title: 'Value',
          field: 'value',
          component: (value, index) => (
            <Dropdown
              id={`detail-list-item-dropdown:${index}`}
              pullRight
              className="column-dropdown"
            >
              <Dropdown.Toggle noCaret>
                <span className="sr-only">More info</span>
                <img className="icon icon-more" alt="" />
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <MenuItem onClick={() => console.log('index', index)}>
                  {value}
                </MenuItem>
              </Dropdown.Menu>
            </Dropdown>
          ),
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withMultipleComponentsColumn = () => {
    const attr = {
      data: [
        {
          name: 'rowName',
          type: 'rowType',
          value: [1],
          key: 'database://cluster.schema/table/rowName',
        },
        {
          name: 'rowName2',
          type: 'rowType2',
          value: [2, 3],
          key: 'database://cluster.schema/table/rowName2',
        },
        {
          name: 'rowName3',
          type: 'rowType3',
          value: [4, 5, 6],
          key: 'database://cluster.schema/table/rowName3',
        },
      ],
      columns: [
        {
          title: 'Name',
          field: 'name',
        },
        {
          title: 'Type',
          field: 'type',
        },
        {
          title: 'Value',
          field: 'value',
          component: (values) =>
            values.map((val) => <strong key={`key:${val}`}>{val}</strong>),
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withAlignedColumns = () => {
    const attr = {
      data: [...this.config.data],
      columns: [
        {
          title: 'Name',
          field: 'name',
          horAlign: 'left',
        },
        {
          title: 'Type',
          field: 'type',
          horAlign: 'center',
        },
        {
          title: 'Value',
          field: 'value',
          horAlign: 'right',
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withFourColumns = () => {
    const attr = {
      data: [
        {
          name: 'rowName',
          type: 'rowType',
          value: 1,
          key: 'database://cluster.schema/table/rowName',
          usage: 4,
        },
        {
          name: 'rowName2',
          type: 'rowType2',
          value: 2,
          key: 'database://cluster.schema/table/rowName2',
          usage: 12,
        },
        {
          name: 'rowName3',
          type: 'rowType3',
          value: 3,
          key: 'database://cluster.schema/table/rowName3',
          usage: 7,
        },
      ],
      columns: [
        {
          title: 'Name',
          field: 'name',
          horAlign: 'left',
        },
        {
          title: 'Type',
          field: 'type',
          horAlign: 'right',
        },
        {
          title: 'Value',
          field: 'value',
          horAlign: 'left',
        },
        {
          title: 'Usage',
          field: 'usage',
          horAlign: 'left',
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withFixedWidthColumns = () => {
    const attr = {
      data: [...this.config.data],
      columns: [
        {
          title: 'Name',
          field: 'name',
          width: 50,
          horAlign: 'left',
        },
        {
          title: 'Type',
          field: 'type',
          width: 200,
          horAlign: 'center',
        },
        {
          title: 'Value',
          field: 'value',
          horAlign: 'right',
        },
      ],
    };

    return new this.Klass(attr);
  };

  this.withEmptyData = () => {
    const attr = {
      data: [],
      columns: [{ title: 'Name', field: 'name' }],
    };

    return new this.Klass(attr);
  };

  this.withMoreDataThanColumns = () => {
    const attr = {
      data: [
        ...this.config.data,
        {
          name: 'extraName',
          type: 'extraRowType',
          value: 4,
          key: 'database://cluster.schema/table/extraName',
          usage: 44,
          extraValue: 3,
        },
      ],
      columns: [...this.config.columns],
    };

    return new this.Klass(attr);
  };

  this.build = () => this.config;
}

export default TestDataBuilder;
