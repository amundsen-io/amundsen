// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

export interface User {
  display_name: string;
  email: string;
  profile_url: string;
  user_id: string;
  other_key_values?: Record<string, string>;
}

// Not a good name, not sure if we can consolidate yet
// TODO: Change to User when ready.
export interface PeopleUser {
  email: string;
  employee_type: string;
  display_name: string;
  first_name: string;
  full_name: string;
  github_username: string;
  is_active: boolean;
  last_name: string;
  // Inconsistent data format from search and metadata return either `manager_email` or `manager_fullname`
  manager_email?: string;
  manager_fullname?: string;
  profile_url: string;
  role_name?: string;
  slack_id: string;
  team_name: string;
  user_id: string;
}

export type LoggedInUser = PeopleUser & {};

export type OwnerDict = { [id: string]: User };
