import { Tag } from '../Tags/types';

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
  reader: User[];
}

interface TableWriter {
  application_url: string;
  description: string;
  id: string;
  name: string;
}

interface User {
  display_name: string;
}

export interface PreviewQueryParams {
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

export interface TableMetadata {
  columns: TableColumn[];
  is_editable: boolean;
  schema: string;
  table_name: string;
  table_description: string;
  table_writer: TableWriter;
  owners: User[];
  partition: PartitionData;
  table_readers: TableReader[];
  tags: Tag[];
  watermarks: Watermark[];
}

export interface Watermark {
  create_time: string;
  partition_key: string;
  partition_value: string;
  watermark_type: string;
}
