// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../StorySection';
import Table from '.';
import TestDataBuilder from './testDataBuilder';

const dataBuilder = new TestDataBuilder();
const { columns, data } = dataBuilder.build();
const {
  columns: alignedColumns,
  data: alignedData,
} = dataBuilder.withAlignedColumns().build();

const stories = storiesOf('Components/Table', module);

stories.add('Table', () => (
  <>
    <StorySection title="Basic Table">
      <Table columns={columns} data={data} />
    </StorySection>
    <StorySection title="Empty Table">
      <Table columns={columns} data={[]} />
    </StorySection>
    <StorySection title="Loading Table">
      <Table columns={[]} data={[]} options={{ isLoading: true }} />
    </StorySection>
    <StorySection title="Table with different column alignment">
      <Table columns={alignedColumns} data={alignedData} />
    </StorySection>
    <StorySection title="Table with 50px row height">
      <Table columns={columns} data={data} options={{ rowHeight: 50 }} />
    </StorySection>
  </>
));
