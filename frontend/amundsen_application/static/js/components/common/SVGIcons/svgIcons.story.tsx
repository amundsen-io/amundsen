import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../StorySection';
import { AlertIcon } from '.';

const stories = storiesOf('Attributes/Icons', module);

stories.add('SVG Icons', () => (
  <>
    <StorySection title="Alert">
      <AlertIcon />
    </StorySection>
  </>
));
