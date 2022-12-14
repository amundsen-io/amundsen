/* eslint-disable no-alert */
// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import { Meta } from '@storybook/react/types-6-0';

import StorySection from '../StorySection';
import { DefinitionList } from '.';

export const DefinitionListStory = (): React.ReactNode => (
  <>
    <StorySection title="DefinitionList">
      <DefinitionList
        definitions={[
          {
            term: 'Table name',
            description: 'coco.fact_rides',
          },
          {
            term: 'Root cause',
            description:
              'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod',
          },
          {
            term: 'Estimate',
            description: 'Target fix by MM/DD/YYYY 00:00',
          },
        ]}
      />
    </StorySection>
    <StorySection title="DefinitionList with html descriptions">
      <DefinitionList
        definitions={[
          {
            term: 'Verity checks',
            description:
              '1 out of 4 checks failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
          },
          {
            term: 'Failed DAGs',
            description:
              '1 out of 4 DAGs failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
          },
        ]}
      />
    </StorySection>
    <StorySection title="DefinitionList with fixed term width">
      <DefinitionList
        termWidth={200}
        definitions={[
          {
            term: 'Table name',
            description: 'coco.fact_rides',
          },
          {
            term: 'Failed DAGs',
            description:
              '1 out of 4 DAGs failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
          },
        ]}
      />
    </StorySection>
  </>
);

DefinitionListStory.storyName = 'with basic options';

export default {
  title: 'Components/DefinitionList',
  component: DefinitionList,
  decorators: [],
} as Meta;
