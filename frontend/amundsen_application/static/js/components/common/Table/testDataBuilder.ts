const defaultData = [
  { name: 'rowName', type: 'rowType', value: 1 },
  { name: 'rowName2', type: 'rowType2', value: 2 },
  { name: 'rowName3', type: 'rowType3', value: 3 },
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

  this.withUsageRow = () => {
    const attr = {
      data: [
        ...this.config.data,
        { name: 'usageRow', type: 'usageRowType', value: 4, usage: 44 },
      ],
      columns: [...this.config.columns, { title: 'Usage', field: 'usage' }],
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
