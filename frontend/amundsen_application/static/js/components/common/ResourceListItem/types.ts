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
  cluster: string;
  database: string;
  description: string;
  key: string;
  // 'popular_tables' currently does not support 'last_updated_epoch'
  last_updated_epoch?: number;
  name: string;
  schema_name: string;
}

/**
 * This is a sample of the user data type which includes all fields.
 * We will only need a subset of this for UserResource.

interface User {
  active : boolean;
  backupCodes: any[]; // Not sure of type
  birthday : string | null;
  department: string;
  department_id: string;
  email: string;
  employment_type: string;
  first_name: string;
  github_username: string;
  hris_active: boolean;
  hris_number: string;
  hris_source : string;
  id: number;
  last_name: string;
  manager_email : string;
  manager_id: number;
  manager_hris_number: string;
  mobile_phone : string | null;
  name : string;
  offboarded : boolean;
  office: string;
  role: string;
  start_date : string;
  team_name: string;
  title: string;
  work_phone: string;
}
*/

// Placeholder until the schema is defined.
export interface UserResource extends Resource  {
  type: ResourceType.user;
  active : boolean;
  birthday : string | null;
  department: string;
  email: string;
  first_name: string;
  github_username: string;
  id: number;
  last_name: string;
  manager_email : string;
  name : string;
  offboarded : boolean;
  office: string;
  role: string;
  start_date : string;
  team_name: string;
  title: string;
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
