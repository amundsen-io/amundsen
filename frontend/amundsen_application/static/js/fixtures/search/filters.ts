import { ResourceType } from 'interfaces';

export const defaultEmptyFilters = {
  [ResourceType.table]: {},
};

export const datasetFilterExample = {
  [ResourceType.table]: {
    schema: { value: 'schema_name' },
    database: { value: 'hive' },
  },
};
