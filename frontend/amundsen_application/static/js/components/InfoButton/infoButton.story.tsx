// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

import { IconSizes } from 'interfaces';
import StorySection from '../StorySection';
import InfoButton from '.';

export const InfoButtonStory = () => (
  <>
    <StorySection title="Info Button">
      <InfoButton infoText="Some info text to share" title="Popover Title" />
    </StorySection>
    <StorySection title="Info Button to left">
      <InfoButton
        infoText="Some info text to share"
        title="Popover Title"
        placement="left"
      />
    </StorySection>
    <StorySection title="Info Button small size">
      <InfoButton
        infoText="Some info text to share"
        title="Popover Title"
        placement="left"
        size={IconSizes.SMALL}
      />
    </StorySection>
  </>
);

InfoButtonStory.storyName = 'Info Button';

export default {
  title: 'Components/Buttons',
  component: InfoButton,
};
