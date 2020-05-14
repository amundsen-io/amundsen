import { UpdateMethod } from './Enums';
import { User } from './User';
import { Badge } from './Tags';

interface PartitionData {
  is_partitioned: boolean;
  key?: string;
  value?: string;
}

interface PreviewColumnItem {
  column_name: string;
  column_type: string;
}

interface PreviewDataItem {
  id: string;
}

export interface TableColumnStats {
  stat_type: string;
  stat_val: string;
  /** The start date of the stat aggregation period, in unix epoch time */
  start_epoch: number;
  /** The end date of the stat aggregation period, in unix epoch time */
  end_epoch: number;
}

// TODO - Make this reusable for dashboards
export interface TableReader {
  read_count: number;
  user: User;
}

export interface TableSource {
  source: string | null;
  source_type: string;
}

export interface TableWriter {
  application_url: string;
  description: string;
  id: string;
  name: string;
}

export interface PreviewQueryParams {
  database: string;
  schema: string;
  tableName: string;
}

export interface PreviewData {
  columns?: PreviewColumnItem[];
  data?: PreviewDataItem[];
  error_text?: string;
}

export interface TableColumn {
  name: string;
  description: string;
  is_editable: boolean;
  col_type: string;
  stats: TableColumnStats[];
}

export interface TableOwners {
  isLoading: boolean;
  owners: User[];
}

export interface ProgrammaticDescription {
  source: string;
  text: string;
}

export interface TableMetadata {
  badges: Badge[];
  cluster: string;
  columns: TableColumn[];
  database: string;
  is_editable: boolean;
  is_view: boolean;
  key: string;
  last_updated_timestamp: number;
  schema: string;
  name: string;
  description: string;
  table_writer: TableWriter;
  partition: PartitionData;
  table_readers: TableReader[];
  source: TableSource;
  watermarks: Watermark[];
  programmatic_descriptions: ProgrammaticDescription[];
}

export interface UpdateOwnerPayload {
  method: UpdateMethod;
  id: string;
}

export interface Watermark {
  create_time: string;
  partition_key: string;
  partition_value: string;
  watermark_type: string;
}
