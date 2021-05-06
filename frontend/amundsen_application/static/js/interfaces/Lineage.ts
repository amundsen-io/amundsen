import { Badge } from './Badges';

export interface LineageItem {
  badges: Badge[];
  cluster: string;
  database: string;
  key: string;
  level: number;
  name: string;
  schema: string;
  parent: string;
  usage: number;
}

export interface Lineage {
  downstream_entities: LineageItem[];
  upstream_entities: LineageItem[];
}

// To keep the backward compatibility for the list based lineage
// ToDo: Please remove once list based view is deprecated
export interface ColumnLineageMap {
  [columnName: string]: {
    lineage: Lineage;
    isLoading: boolean;
  };
}

export interface TableLineageParams {
  key: string;
}

export interface ColumnLineageParams {
  key: string;
  column: string;
}
