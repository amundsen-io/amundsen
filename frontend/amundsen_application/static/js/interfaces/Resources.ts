import { PeopleUser } from 'interfaces/User';

export enum ResourceType {
  table = "table",
  user = "user",
  dashboard = "dashboard",
};

export const DEFAULT_RESOURCE_TYPE = ResourceType.table;

export interface Resource {
  type: ResourceType;
};

// Placeholder until the schema is defined.
export interface DashboardResource extends Resource  {
  type: ResourceType.dashboard;
  title: string;
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
};

export interface UserResource extends Resource, PeopleUser {
  type: ResourceType.user;
}

// TODO - Consider just using the 'Resource' type instead
export type Bookmark = TableResource & {};
