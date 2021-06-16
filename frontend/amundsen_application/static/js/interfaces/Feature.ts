import { User } from 'interfaces/User';
import { Badge } from 'interfaces/Badges';
import { Tag } from 'interfaces/Tags';
import {
  ProgrammaticDescription,
  TableColumn,
  Watermark,
} from 'interfaces/TableMetadata';

export interface FeatureMetadata {
  availability: string[];
  badges: Badge[];
  created_timestamp: number;
  data_type?: string;
  description: string;
  entity?: string;
  feature_group: string;
  key: string;
  last_updated_timestamp: number;
  name: string;
  owners: User[];
  partition_column?: string;
  programmatic_descriptions: ProgrammaticDescription[];
  stats: FeatureStats[];
  status: string;
  tags: Tag[];
  version: string;
  watermarks: Watermark[];
}

// TODO - duplicated with FeatureResource in Resources.ts. Might delete this.
export interface FeatureSummary {
  key: string;
  name: string;
  version: string;
  availability: string[];
  entity?: string[];
  description: string;
}

// TODO - Figure out if we can reuse ColumnStats
export interface FeatureStats {
  name: string;
}
