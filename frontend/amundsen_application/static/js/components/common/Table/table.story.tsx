// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../StorySection';
import Table from '.';
import TestDataBuilder from './testDataBuilder';

const { columns, data } = new TestDataBuilder().build();

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
  </>
));
