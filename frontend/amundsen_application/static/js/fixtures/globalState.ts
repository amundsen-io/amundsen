import { GlobalState } from 'ducks/rootReducer';
import { ResourceType, SendingState } from 'interfaces';

import { defaultEmptyFilters } from './search/filters';

const globalState: GlobalState = {
  announcements: {
      posts: [{
        date: '12/31/1999',
        title: 'Y2K',
        html_content: '<div>The end of the world</div>',
      },
      {
        date: '01/01/2000',
        title: 'False Alarm',
        html_content: '<div>Just kidding</div>',
      }],
  },
  bookmarks: {
    myBookmarks: [
      {
        key: 'bookmarked_key',
        type: ResourceType.table,
        cluster: 'cluster',
        database: 'database',
        description: 'description',
        name: 'name',
        schema: 'schema',
      },
    ],
    myBookmarksIsLoaded: false,
    bookmarksForUser: [],
  },
  feedback: {
    sendState: SendingState.IDLE,
  },
  issue: {
    issues: [], 
    remainingIssuesUrl: null, 
    remainingIssues: 0,
    isLoading: true
  }, 
  notification: {
    requestIsOpen: false,
    sendState: SendingState.IDLE,
  },
  popularTables: [
    {
      cluster: 'testCluster',
      database: 'testDatabase',
      description: 'I have a lot of users',
      key: 'testDatabase://testCluster.testSchema/testName',
      name: 'testName',
      schema: 'testSchema',
      type: ResourceType.table,
    },
    {
      cluster: 'testCluster',
      database: 'testDatabase',
      description: 'I also have a lot of users',
      key: 'testDatabase://testCluster.testSchema/otherName',
      name: 'otherName',
      schema: 'testSchema',
      type: ResourceType.table,
    }
  ],
  search: {
    search_term: 'testName',
    selectedTab: ResourceType.table,
    isLoading: false,
    dashboards: {
      page_index: 0,
      results: [],
      total_results: 0,
    },
    tables: {
      page_index: 0,
      results: [
        {
          cluster: 'testCluster',
          database: 'testDatabase',
          description: 'I have a lot of users',
          key: 'testDatabase://testCluster.testSchema/testName',
          last_updated_timestamp: 946684799,
          name: 'testName',
          schema: 'testSchema',
          type: ResourceType.table,
        },
      ],
      total_results: 1,
    },
    users: {
      page_index: 0,
      results: [],
      total_results: 0,
    },
    inlineResults: {
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
    },
    filters: defaultEmptyFilters,
  },
  tableMetadata: {
    isLoading: true,
    lastIndexed: 1555632106,
    preview: {
      data: {},
      status: null,
    },
    statusCode: null,
    tableData: {
      badges: [],
      cluster: '',
      columns: [],
      database: '',
      is_editable: false,
      is_view: false,
      key: '',
      last_updated_timestamp: 0,
      schema: '',
      name: '',
      description: '',
      table_writer: { application_url: '', description: '', id: '', name: '' },
      partition: { is_partitioned: false },
      table_readers: [],
      source: { source: '', source_type: '' },
      watermarks: [],
      programmatic_descriptions: []
    },
    tableOwners: {
      isLoading: true,
      owners: {},
    },
    tableTags: {
      isLoading: true,
      tags: [],
    },
  },
  allTags: {
    allTags: [
      {
        tag_name: 'curated_tag_1',
        tag_count: 20,
      },
      {
        tag_name: 'other_tag_1',
        tag_count: 15,
      }
    ],
    isLoading: false,
  },
  user:  {
    loggedInUser: {
      display_name: 'firstname lastname',
      email: 'test@test.com',
      employee_type: 'fulltime',
      first_name: 'firstname',
      full_name: 'firstname lastname',
      github_username: 'githubName',
      is_active: true,
      last_name: 'lastname',
      manager_fullname: 'Test Manager',
      profile_url: 'www.test.com',
      role_name: 'Tester',
      slack_id: 'www.slack.com',
      team_name: 'QA',
      user_id: 'test0',
    },
    profile: {
      own: [
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
      ],
      read: [
        { type: ResourceType.table },
        { type: ResourceType.table },
      ],
      user: {
        display_name: 'firstname lastname',
        email: 'test@test.com',
        employee_type: 'fulltime',
        first_name: 'firstname',
        full_name: 'firstname lastname',
        github_username: 'githubName',
        is_active: true,
        last_name: 'lastname',
        manager_fullname: 'Test Manager',
        profile_url: 'www.test.com',
        role_name: 'Tester',
        slack_id: 'www.slack.com',
        team_name: 'QA',
        user_id: 'test0',
      },
    },
  },
};

export default globalState;
