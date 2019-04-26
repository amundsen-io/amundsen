import { GlobalState } from 'ducks/rootReducer';
import { SendingState } from 'components/Feedback/types';

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
  feedback: {
      sendState: SendingState.IDLE,
  },
  popularTables: [],
  search: {
    search_term: '',
    dashboards: {
      page_index: 0,
      results: [],
      total_results: 0,
    },
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
  tableMetadata: {
    isLoading: true,
    lastIndexed: 1555632106,
    preview: {
      data: {},
      status: null,
    },
    statusCode: null,
    tableData: {
      cluster: '',
      columns: [],
      database: '',
      is_editable: false,
      is_view: false,
      schema: '',
      table_name: '',
      table_description: '',
      table_writer: { application_url: '', description: '', id: '', name: '' },
      partition: { is_partitioned: false },
      table_readers: [],
      source: { source: '', source_type: '' },
      watermarks: [],
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
    allTags: [],
    isLoading: false,
  },
  user:  {
    loggedInUser: {
      user_id: 'user0',
      display_name: 'User Name',
    },
    profileUser: {
      user_id: 'user1',
      display_name: 'User1 Name',
    },
  },
};

export default globalState;
