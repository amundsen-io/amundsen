// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

import StorySection from '../StorySection';

export const BootstrapButtonStory = () => (
  <>
    <StorySection title="Button">
      <button type="button" className="btn">
        Button
      </button>
    </StorySection>
    <StorySection title="Button Default">
      <button type="button" className="btn btn-default">
        Button Default
      </button>
    </StorySection>
    <StorySection title="Button on Link">
      {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
      <a href="#" className="btn">
        Button on Link
      </a>
    </StorySection>
    <StorySection title="Link Button">
      <button type="button" className="btn btn-link">
        Link Button
      </button>
    </StorySection>
    <StorySection title="Block Button">
      <button type="button" className="btn btn-block">
        Button Block
      </button>
    </StorySection>
    <StorySection title="Button Sizes">
      <button type="button" className="btn btn-lg">
        Large Button
      </button>
      <button type="button" className="btn btn-sm">
        Small Button
      </button>
      <button type="button" className="btn btn-xs">
        Extra Small Button
      </button>
    </StorySection>

    <StorySection title="Button Success">
      <button type="button" className="btn btn-success">
        Button Success
      </button>
    </StorySection>
    <StorySection title="Button Info">
      <button type="button" className="btn btn-info">
        Button Info
      </button>
    </StorySection>
    <StorySection title="Button Warning">
      <button type="button" className="btn btn-warning">
        Button Warning
      </button>
    </StorySection>
    <StorySection title="Button Danger">
      <button type="button" className="btn btn-danger">
        Button Danger
      </button>
    </StorySection>
  </>
);

BootstrapButtonStory.storyName = 'Bootstrap Buttons';

export default {
  title: 'Components/Buttons',
};
