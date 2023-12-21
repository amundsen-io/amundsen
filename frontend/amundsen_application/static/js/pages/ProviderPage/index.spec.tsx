// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as History from 'history';
import { shallow } from 'enzyme';

import { getMockRouterProps } from 'fixtures/mockRouter';
import { tableMetadata, tableLineage } from 'fixtures/metadata/table';
import { snowflakeTableShares } from 'fixtures/metadata/snowflake';

import LoadingSpinner from 'components/LoadingSpinner';
import TabsComponent from 'components/TabsComponent';

import * as ConfigUtils from 'config/config-utils';

import { PROVIDER_TABS } from './constants';
//import { TableDetail, TableDetailProps, MatchProps } from '.';

import { STATUS_CODES } from '../../constants';

const mockColumnDetails = {
  content: {
    title: 'column_name',
    description: 'description',
    nestedLevel: 0,
    hasStats: true,
  },
  type: { name: 'column_name', database: 'database', type: 'string' },
  usage: 0,
  stats: [
    {
      end_epoch: 1600473600,
      start_epoch: 1597881600,
      stat_type: 'column_usage',
      stat_val: '111',
    },
  ],
  children: [],
  action: { name: 'column_name', isActionEnabled: true },
  editText: 'Click to edit description in the data source site',
  editUrl: 'https://test.datasource.site/table',
  index: 0,
  key: 'database://cluster.schema/table/column_name',
  name: 'column_name',
  tableParams: {
    database: 'database',
    cluster: 'cluster',
    schema: 'schema',
    table: 'table',
  },
  sort_order: 0,
  isEditable: true,
  isExpandable: false,
  badges: [
    {
      badge_name: 'Badge Name 1',
      category: 'column',
    },
  ],
  typeMetadata: {
    kind: 'scalar',
    name: 'column_name',
    key: 'database://cluster.schema/table/column_name/type/column_name',
    description: 'description',
    data_type: 'string',
    sort_order: 0,
    is_editable: true,
  },
};
