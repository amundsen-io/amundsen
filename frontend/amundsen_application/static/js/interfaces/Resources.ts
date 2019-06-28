import { PeopleUser } from 'interfaces/User';

export enum ResourceType {
  table = "table",
  user = "user",
  dashboard = "dashboard",
};

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
  // 'popular_tables' currently does not support 'last_updated_epoch'
  last_updated_epoch?: number;
  name: string;
  schema_name: string;
};

export interface UserResource extends Resource, PeopleUser {
  type: ResourceType.user;
}

// TODO - Consider just using the 'Resource' type instead
export type Bookmark = TableResource & {};
