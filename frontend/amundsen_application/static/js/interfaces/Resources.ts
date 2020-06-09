import { PeopleUser } from './User';
import { Badge } from './Tags';

export enum ResourceType {
  table = 'table',
  user = 'user',
  dashboard = 'dashboard',
  query = 'query',
}

export const DEFAULT_RESOURCE_TYPE = ResourceType.table;

export interface Resource {
  type: ResourceType;
}

export interface DashboardResource extends Resource {
  type: ResourceType.dashboard;
  cluster: string;
  description: string;
  group_name: string;
  group_url: string;
  last_successful_run_timestamp: number;
  name: string;
  product: string;
  uri: string;
  url: string;
  // Bookmark logic is cleaner if all resources can settle on either "key" or "uri"
  key?: string;
}

export interface TableResource extends Resource {
  type: ResourceType.table;
  cluster: string;
  database: string;
  description: string;
  key: string;
  // 'popular_tables' currently does not support 'last_updated_timestamp'
  last_updated_timestamp?: number;
  name: string;
  schema: string;
  schema_description?: string;
  badges?: Badge[];
}

export interface UserResource extends Resource, PeopleUser {
  type: ResourceType.user;
}

export interface QueryResource extends Resource {
  type: ResourceType.query;
  name: string;
  query_text: string;
  url: string;
}

export interface ResourceDict<T> {
  [ResourceType.table]: T;
  [ResourceType.dashboard]?: T;
}

// TODO - Consider just using the 'Resource' type instead
export type Bookmark = TableResource | DashboardResource;
