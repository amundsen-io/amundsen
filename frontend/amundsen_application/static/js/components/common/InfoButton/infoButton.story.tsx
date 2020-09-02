// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../StorySection';
import InfoButton from '.';

const stories = storiesOf('Components/Buttons', module);

stories.add('Info Button', () => (
  <>
    <StorySection title="Info Button">
      <InfoButton infoText="Some info text to share" title="Popover Title" />
    </StorySection>
    <StorySection title="Info Button to left">
      <InfoButton
        infoText="Some info text to share"
        title="Popover Title"
        placement="left"
        size="size"
      />
    </StorySection>
    <StorySection title="Info Button small size">
      <InfoButton
        infoText="Some info text to share"
        title="Popover Title"
        placement="left"
        size="small"
      />
    </StorySection>
  </>
));
