// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

import { Binoculars } from 'components/SVGIcons';

import StorySection from '../StorySection';

export const CustomButtonStory = () => (
  <>
    <StorySection title="Button Primary">
      <button type="button" className="btn btn-primary">
        Button Primary
      </button>
      <button type="button" className="btn btn-primary btn-lg">
        Button Primary Large
      </button>
    </StorySection>
    <StorySection title="Button Default">
      <button type="button" className="btn btn-default">
        Button Default
      </button>
      <button type="button" className="btn btn-default btn-lg muted">
        Button Default Muted
      </button>
    </StorySection>
    <StorySection title="Button Flat Icon">
      <button type="button" className="btn btn-flat-icon">
        <span className="sr-only">Flat Icon</span>
        <img className="icon icon-small icon-edit" alt="" />
        Button Flat Icon
      </button>
    </StorySection>
    <StorySection title="Button Flat Icon Dark">
      <button type="button" className="btn btn-flat-icon-dark">
        <span className="sr-only">Flat Icon Dark</span>
        <img className="icon icon-small icon-edit" alt="" />
        Button Flat Icon Dark
      </button>
    </StorySection>
    <StorySection title="Button Close">
      <button type="button" className="btn btn-close">
        <span className="sr-only">Button Close</span>
      </button>
    </StorySection>
    <StorySection title="Button Nav Bar Icon">
      <div className="nav-bar" style={{ backgroundColor: 'blue' }}>
        <div className="ml-auto nav-bar-right">
          <button className="btn btn-nav-bar-icon btn-flat-icon" type="button">
            <Binoculars fill="white" />
            <span className="sr-only">Product Tour</span>
          </button>
        </div>
      </div>
    </StorySection>
    <StorySection title="Button Group">
      <div className="btn-group" role="group">
        <span className="sr-only">Group Message</span>
        <button type="button" className="btn btn-default active">
          Rating
        </button>
        <button type="button" className="btn btn-default">
          Bug
        </button>
        <button type="button" className="btn btn-default">
          Request{' '}
        </button>
      </div>
    </StorySection>
  </>
);

CustomButtonStory.storyName = 'Custom Buttons';

export default {
  title: 'Components/Buttons',
};
