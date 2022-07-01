// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import {
  TableColumn,
  TableColumnStats,
  TypeMetadata,
} from 'interfaces/TableMetadata';
import { Badge } from 'interfaces/Badges';
import { TablePageParams } from '../utils/navigationUtils';

export type ContentType = {
  title: string;
  description: string;
  hasStats: boolean;
};

type DatatypeType = {
  name: string;
  database: string;
  type: string;
};

export type FormattedDataType = {
  content: ContentType;
  type: DatatypeType;
  usage: number | null;
  stats: TableColumnStats[] | null;
  children: TableColumn[] | TypeMetadata[];
  editText: string | null;
  editUrl: string | null;
  index: number;
  key: string;
  name: string;
  tableParams: TablePageParams;
  sort_order: number;
  isEditable: boolean;
  isExpandable: boolean;
  badges: Badge[];
  typeMetadata?: TypeMetadata;
  isNestedColumn?: boolean;
  kind?: string;
};
