export interface User {
  display_name: string;
  profile_url: string;
};

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
  manager_fullname: string;
  profile_url: string;
  role_name?: string;
  slack_id: string;
  team_name: string;
  user_id: string;
};

export type LoggedInUser = PeopleUser & {};
