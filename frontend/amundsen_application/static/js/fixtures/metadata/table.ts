import {
  TableMetadata,
  DashboardResource,
  ResourceType,
} from '../../interfaces';
import { TagType } from '../../interfaces/Tags';

export const tableMetadata: TableMetadata = {
  badges: [
    {
      tag_name: 'ga',
      tag_type: TagType.BADGE,
    },
  ],
  cluster: 'gold',
  columns: [
    {
      col_type: 'bigint',
      description: 'Test Value',
      is_editable: true,
      name: 'ride_id',
      stats: [
        {
          end_epoch: 1588896000,
          start_epoch: 1588896000,
          stat_type: 'count',
          stat_val: '992487',
        },
        {
          end_epoch: 1588896000,
          start_epoch: 1588896000,
          stat_type: 'count_null',
          stat_val: '0',
        },
        {
          end_epoch: 1588896000,
          start_epoch: 1588896000,
          stat_type: 'count_distinct',
          stat_val: '992487',
        },
      ],
    },
    {
      col_type: 'string',
      description:
        'ds will be the date part of requested_at ds will be the date part of requested_at ds will be the date part of requested_at ds will be the date part of requested_at ds will be the date part of requested_at ds will be the date part of requested_at ds w',
      is_editable: true,
      name: 'ds',
      stats: [],
    },
    {
      col_type: 'string',
      description: null,
      is_editable: true,
      name: 'route_id',
      stats: [
        {
          end_epoch: 1588896000,
          start_epoch: 1588896000,
          stat_type: 'count',
          stat_val: '992487',
        },
        {
          end_epoch: 1588896000,
          start_epoch: 1588896000,
          stat_type: 'count_null',
          stat_val: '0',
        },
        {
          end_epoch: 1588896000,
          start_epoch: 1588896000,
          stat_type: 'count_distinct',
          stat_val: '992405',
        },
        {
          end_epoch: 1586476800,
          start_epoch: 1586476800,
          stat_type: 'len_max',
          stat_val: '24',
        },
        {
          end_epoch: 1586476800,
          start_epoch: 1586476800,
          stat_type: 'len_min',
          stat_val: '24',
        },
        {
          end_epoch: 1586476800,
          start_epoch: 1586476800,
          stat_type: 'len_avg',
          stat_val: '24',
        },
      ],
    },
  ],
  database: 'hive',
  description:
    'One row per ride request, showing all stages of the ride funnel. ',
  is_editable: true,
  is_view: false,
  key: 'hive://gold.base/rides',
  last_updated_timestamp: 1583469780,
  name: 'rides',
  partition: {
    is_partitioned: true,
    key: 'ds',
    value: '2020-03-05',
  },
  programmatic_descriptions: [],
  schema: 'base',
  source: {
    source:
      'https://github.com/lyft/etl/blob/master/sql/hive/base/rides.config',
    source_type: 'github',
  },
  table_readers: [
    {
      read_count: 1735,
      user: {
        email: 'testEmail@lyft.com',
        user_id: '123test',
        display_name: 'Test User The First',
        profile_url: 'http://ProfileURLForTest.one',
      },
    },
    {
      read_count: 229,
      user: {
        email: 'testEmailBis@lyft.com',
        user_id: '456test',
        display_name: 'Test User The Second',
        profile_url: 'http://ProfileURLForTest.two',
      },
    },
    {
      read_count: 189,
      user: {
        email: 'testEmailTri@lyft.com',
        user_id: '789test',
        display_name: 'Test User The Third',
        profile_url: 'http://ProfileURLForTest.three',
      },
    },
  ],
  table_writer: {
    application_url:
      'https://etl-production.lyft.net/admin/airflow/tree?dag_id=ADHOC - root',
    description: 'Airflow with id ADHOC - root/UNKNOWN',
    id: 'ADHOC - root/UNKNOWN',
    name: 'Airflow',
  },
  watermarks: [
    {
      create_time: '2020-02-13 19:55:13',
      partition_key: 'ds',
      partition_value: '2020-03-05',
      watermark_type: 'high_watermark',
    },
    {
      create_time: '2020-02-13 19:55:13',
      partition_key: 'ds',
      partition_value: '2013-02-10',
      watermark_type: 'low_watermark',
    },
  ],
};

export const relatedDashboards: DashboardResource[] = [
  {
    group_name: 'Test Group 1',
    description: null,
    cluster: 'gold',
    group_url: 'https://app.mode.com/testCompany/spaces/1234',
    uri: 'mode_dashboard://gold.1234/23445asb',
    last_successful_run_timestamp: 1590505846,
    name: 'Test Dashboard 1',
    product: 'mode',
    type: ResourceType.dashboard,
    url: 'https://app.mode.com/testCompany/reports/23445asb',
  },
  {
    group_name: 'Test Group 2',
    description: null,
    cluster: 'gold',
    group_url: 'https://app.mode.com/testCompany/spaces/345asd',
    uri: 'mode_dashboard://gold.345asd/asdfas001',
    last_successful_run_timestamp: 1590519704,
    name: 'Test Dashboard 2',
    product: 'mode',
    type: ResourceType.dashboard,
    url: 'https://app.mode.com/testCompany/reports/asdfas001',
  },
  {
    group_name: 'Test Group 3',
    description: null,
    cluster: 'gold',
    group_url: 'https://app.mode.com/testCompany/spaces/casdg80',
    uri: 'mode_dashboard://gold.casdg80/123566',
    last_successful_run_timestamp: 1590538191,
    name: 'Test Dashboard 3',
    product: 'mode',
    type: ResourceType.dashboard,
    url: 'https://app.mode.com/testCompany/reports/123566',
  },
];
