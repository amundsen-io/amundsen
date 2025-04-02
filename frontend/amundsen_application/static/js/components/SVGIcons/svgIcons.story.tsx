// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

import StorySection from '../StorySection';
import {
  AlertIcon,
  DownIcon,
  UpIcon,
  RightIcon,
  LeftIcon,
  InformationIcon,
  GridIcon,
  GraphIcon,
} from '.';

export const SVGIcons = () => (
  <>
    <StorySection title="Alert">
      <AlertIcon stroke="currentColor" />
    </StorySection>
    <StorySection title="Down">
      <DownIcon fill="#9191A8" />
    </StorySection>
    <StorySection title="Up">
      <UpIcon fill="#9191A8" />
    </StorySection>
    <StorySection title="Right">
      <RightIcon fill="#9191A8" />
    </StorySection>
    <StorySection title="Left">
      <LeftIcon fill="#9191A8" />
    </StorySection>
    <StorySection title="Information">
      <InformationIcon fill="#9191A8" />
    </StorySection>
    <StorySection title="Grid">
      <GridIcon fill="#9191A8" />
    </StorySection>
    <StorySection title="Graph">
      <GraphIcon fill="#9191A8" />
    </StorySection>
  </>
);

SVGIcons.storyName = 'SVG Icons';

export default {
  title: 'Attributes/Iconography',
  component: AlertIcon,
};
