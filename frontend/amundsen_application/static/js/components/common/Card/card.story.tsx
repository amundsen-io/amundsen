import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../StorySection';
import Card from '.';

const stories = storiesOf('Components/Cards', module);

stories.add('Cards', () => (
  <>
    <StorySection title="Loading Card">
      <Card isLoading />
    </StorySection>
    <StorySection title="Basic Card">
      <Card
        title="Card Title"
        copy="Lorem, ipsum dolor sit amet consectetur adipisicing elit. Minima autem dolorum incidunt quaerat perspiciatis! Totam est, ab molestiae magnam quisquam eligendi enim eum, iste excepturi mollitia laboriosam cumque, vitae reiciendis."
      />
    </StorySection>
    <StorySection title="Full Card">
      <Card
        title="Card Title"
        subtitle="Card Subtitle"
        copy="Lorem, ipsum dolor sit amet consectetur adipisicing elit. Minima autem dolorum incidunt quaerat perspiciatis! Totam est, ab molestiae magnam quisquam eligendi enim eum, iste excepturi mollitia laboriosam cumque, vitae reiciendis."
      />
    </StorySection>
  </>
));
