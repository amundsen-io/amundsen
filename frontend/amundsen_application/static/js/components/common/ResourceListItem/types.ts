export enum ResourceType {
  table = "table",
  user = "user",
  dashboard = "dashboard",
}

export interface Resource {
  type: ResourceType;
}

export interface TableResource extends Resource {
  type: ResourceType.table;
  database: string;
  cluster: string;
  description: string;
  key: string;
  last_updated: number;
  name: string;
  schema_name: string;
}

// Placeholder until the schema is defined.
export interface UserResource extends Resource  {
  type: ResourceType.user;
  first_name: string;
  last_name: string;
  email: string;
}

// Placeholder until the schema is defined.
export interface DashboardResource extends Resource  {
  type: ResourceType.dashboard;
  title: string;
}

export interface LoggingParams {
  source: string;
  index: number;
}
