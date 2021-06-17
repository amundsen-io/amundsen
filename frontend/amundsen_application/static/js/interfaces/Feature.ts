import { User } from 'interfaces/User';
import { Badge } from 'interfaces/Badges';
import { Tag } from 'interfaces/Tags';
import { ProgrammaticDescription } from 'interfaces/TableMetadata';

export interface FeatureMetadata {
  key: string;
  name: string;
  version: string;
  status: string;
  feature_group: string;
  entity?: string;
  data_type?: string;
  availability: string[];
  description: string;
  owners: User[];
  badges: Badge[];
  owner_tags?: Tag[];
  tags: Tag[];
  programmatic_descriptions: ProgrammaticDescription[];
  watermarks: FeatureWatermark[];
  stats: FeatureStats[];
  last_updated_timestamp: number;
  created_timestamp: number;
  partition_column?: string;
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

export interface FeatureWatermark {
  key: string;
  watermark_type: string;
  time: string;
}
