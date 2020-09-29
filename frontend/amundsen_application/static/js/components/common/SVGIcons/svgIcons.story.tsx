// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { withKnobs, object } from '@storybook/addon-knobs';

import StorySection from '../StorySection';
import { AlertIcon, DownIcon, UpIcon, RightIcon } from '.';

export const SVGIcons = () => (
  <>
    <StorySection title="Alert">
      <AlertIcon stroke={object('Alert stroke', 'currentColor')} />
    </StorySection>
    <StorySection title="Down">
      <DownIcon
        stroke={object('DownIcon stroke', 'currentColor')}
        fill={object('DownIcon fill', '#9191A8')}
      />
    </StorySection>
    <StorySection title="Up">
      <UpIcon
        stroke={object('UpIcon stroke', 'currentColor')}
        fill={object('UpIcon fill', '#9191A8')}
      />
    </StorySection>
    <StorySection title="Right">
      <RightIcon
        stroke={object('RightIcon stroke', 'currentColor')}
        fill={object('RightIcon fill', '#9191A8')}
      />
    </StorySection>
  </>
);
SVGIcons.storyName = 'SVG Icons';

export default {
  title: 'Attributes/Iconography',
  component: AlertIcon,
  decorators: [withKnobs],
};
