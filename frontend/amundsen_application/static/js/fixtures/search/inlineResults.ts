import { ResourceType } from 'interfaces';

export const isLoadingExample = {
  isLoading: true,
  tables: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
  users: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
};

export const noResultsExample = {
  isLoading: false,
  tables: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
  users: {
    page_index: 0,
    results: [],
    total_results: 0,
  },
};

export const allResourcesExample = {
  isLoading: false,
  tables: {
    page_index: 0,
    results: [
      {
        cluster: 'testCluster',
        database: 'testDatabase',
        description: 'I have a lot of users',
        key: 'testDatabase://testCluster.testSchema/testName1',
        last_updated_timestamp: 946684799,
        name: 'testName1',
        schema: 'testSchema',
        type: ResourceType.table,
      },
      {
        cluster: 'testCluster',
        database: 'testDatabase',
        description: 'I have a lot of users',
        key: 'testDatabase://testCluster.testSchema/testName2',
        last_updated_timestamp: 946684799,
        name: 'testName2',
        schema: 'testSchema',
        type: ResourceType.table,
      },
      {
        cluster: 'testCluster',
        database: 'testDatabase',
        description: 'I have a lot of users',
        key: 'testDatabase://testCluster.testSchema/testName3',
        last_updated_timestamp: 946684799,
        name: 'testName3',
        schema: 'testSchema',
        type: ResourceType.table,
      }
    ],
    total_results: 3,
  },
  users: {
    page_index: 0,
    results: [
      {
        display_name: 'Test User',
        email: 'tuser@test.com',
        employee_type: null,
        first_name: 'Test',
        full_name: 'Test User',
        github_username: '',
        is_active: true,
        last_name: 'User',
        manager_email: 'tuser2@test.com',
        manager_fullname: 'Test User2',
        profile_url: '',
        role_name: null,
        slack_id: null,
        team_name: 'Amundsen Team',
        type: 'user',
        user_id: 'tuser@test.com'
      },
      {
        display_name: 'Test User2',
        email: 'tuser2@test.com',
        employee_type: null,
        first_name: 'Test',
        full_name: 'Test User2',
        github_username: '',
        is_active: true,
        last_name: 'User2',
        manager_email: 'tuser3@test.com',
        manager_fullname: 'Test User3',
        profile_url: '',
        role_name: null,
        slack_id: null,
        team_name: 'Amundsen Team',
        type: 'user',
        user_id: 'tuser2@test.com'
      }
    ],
    total_results: 2,
  },
};
