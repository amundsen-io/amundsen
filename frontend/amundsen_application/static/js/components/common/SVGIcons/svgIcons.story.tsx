// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../StorySection';
import { AlertIcon, DownIcon, UpIcon } from '.';

const stories = storiesOf('Attributes/Iconography', module);

stories.add('SVG Icons', () => (
  <>
    <StorySection title="Alert">
      <AlertIcon />
    </StorySection>
    <StorySection title="Down">
      <DownIcon />
    </StorySection>
    <StorySection title="Up">
      <UpIcon />
    </StorySection>
  </>
));
