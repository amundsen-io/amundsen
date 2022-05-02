// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { storiesOf } from '@storybook/react';

import StorySection from '../components/StorySection';

const stories = storiesOf('Attributes/Colors', module);

const COLOR_BLOCK_SIZE = '80px';

type ColorBlockProps = {
  color: string;
  title: string;
};

const ColorBlock: React.FC<ColorBlockProps> = ({
  color,
  title,
}: ColorBlockProps) => (
  <div style={{ margin: '20px' }}>
    <h3 className="text-subtitle-w2">{title}</h3>
    <div
      style={{
        width: COLOR_BLOCK_SIZE,
        height: COLOR_BLOCK_SIZE,
        backgroundColor: `${color}`,
        borderRadius: '3px',
      }}
    />
  </div>
);

stories.add('Colors', () => (
  <>
    <StorySection title="Brand Colors">
      <div style={{ display: 'flex' }}>
        <ColorBlock title="$brand-color-1" color="#B6E7FD" />
        <ColorBlock title="$brand-color-2" color="#6DCFFC" />
        <ColorBlock title="$brand-color-3" color="#00ABFA" />
        <ColorBlock title="$brand-color-4" color="#007DFB" />
        <ColorBlock title="$brand-color-5" color="#0666EB" />
      </div>
    </StorySection>
    <StorySection title="Text Colors">
      <div style={{ display: 'flex' }}>
        <ColorBlock title="$text-primary" color="#21262E" />
        <ColorBlock title="$text-secondary" color="#4E5867" />
        <ColorBlock title="$text-tertiary" color="#99A2AF" />
        <ColorBlock title="$text-placeholder" color="#99A2AF" />
        <ColorBlock title="$text-inverse" color="#FFFFFF" />
      </div>
    </StorySection>
  </>
));
