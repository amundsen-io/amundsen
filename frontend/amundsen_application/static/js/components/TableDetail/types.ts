import { Tag } from 'components/Tags/types';

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

interface TableColumnStats {
  stat_type: string;
  stat_val: string;
  /** The start date of the stat aggregation period, in unix epoch time */
  start_epoch: string;
  /** The end date of the stat aggregation period, in unix epoch time */
  end_epoch: string;
}

interface TableReader {
  read_count: number;
  reader: User;
}

interface TableSource {
  source: string | null;
  source_type: string;
}

interface TableWriter {
  application_url: string;
  description: string;
  id: string;
  name: string;
}

export interface User {
  display_name: string;
  profile_url: string;
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
  type: string;
  stats: TableColumnStats[];
}

export interface TableOwners {
  isLoading: boolean;
  owners: User[];
}

export interface TableMetadata {
  cluster: string;
  columns: TableColumn[];
  database: string;
  is_editable: boolean;
  is_view: boolean;
  schema: string;
  table_name: string;
  table_description: string;
  table_writer: TableWriter;
  partition: PartitionData;
  table_readers: TableReader[];
  source: TableSource;
  watermarks: Watermark[];
}

export interface Watermark {
  create_time: string;
  partition_key: string;
  partition_value: string;
  watermark_type: string;
}
