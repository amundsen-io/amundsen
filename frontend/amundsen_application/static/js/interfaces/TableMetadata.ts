import { UpdateMethod } from './Enums';
import { User } from './User';
import { Badge } from './Badges';

interface PartitionData {
  is_partitioned: boolean;
  key?: string;
  value?: string;
}

export interface TableColumnStats {
  stat_type: string;
  stat_val: string;
  /** The start date of the stat aggregation period, in unix epoch time */
  start_epoch: number;
  /** The end date of the stat aggregation period, in unix epoch time */
  end_epoch: number;
}

export interface ColumnUniqueValues {
  value: string;
  count: number;
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

export interface TableApp {
  application_url: string;
  description: string;
  id: string;
  name: string;
  kind?: string;
}

export interface TablePreviewQueryParams {
  database: string;
  schema: string;
  tableName: string;
  cluster: string;
}

export interface TableColumn {
  badges: Badge[];
  col_type: string;
  description: string;
  is_editable: boolean;
  key?: string;
  name: string;
  type_metadata?: TypeMetadata;
  sort_order: number;
  stats: TableColumnStats[];
}

export interface TypeMetadata {
  kind: string;
  name: string;
  key: string;
  description: string;
  data_type: string;
  sort_order: number;
  badges?: Badge[];
  children?: TypeMetadata[];
  is_editable: boolean;
}

export interface TableOwners {
  isLoading: boolean;
  owners: User[];
}

export interface ProgrammaticDescription {
  source: string;
  text: string;
}
export interface TableProgrammaticDescriptions {
  left?: ProgrammaticDescription[];
  right?: ProgrammaticDescription[];
  other?: ProgrammaticDescription[];
}

export interface ResourceReport {
  name: string;
  url: string;
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
  table_writer: TableApp;
  table_apps?: TableApp[];
  partition: PartitionData;
  table_readers: TableReader[];
  source: TableSource;
  resource_reports: ResourceReport[];
  watermarks: Watermark[];
  programmatic_descriptions: TableProgrammaticDescriptions;
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

export interface TableQualityChecks {
  external_url: string;
  last_run_timestamp: number | null;
  num_checks_success: number;
  num_checks_failed: number;
  num_checks_total: number;
}
