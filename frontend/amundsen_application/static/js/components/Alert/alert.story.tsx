/* eslint-disable no-alert */
// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';
import { Meta } from '@storybook/react/types-6-0';

import { NoticeSeverity } from 'config/config-types';

import StorySection from '../StorySection';
import { Alert, AlertList } from '.';

export const AlertStory = (): React.ReactNode => (
  <>
    <StorySection title="Alert">
      <Alert
        message="Alert text that can be short"
        onAction={() => {
          alert('action executed!');
        }}
      />
    </StorySection>
    <StorySection title="Alert with long text">
      <Alert message="Lorem ipsum dolor sit amet consectetur adipisicing elit. Laboriosam perspiciatis non ipsa officia expedita magnam mollitia, excepturi iste eveniet qui nisi eum illum, quas voluptas, reprehenderit quam molestias cum quisquam!" />
    </StorySection>
    <StorySection title="Alert with long text and action">
      <Alert
        actionText="Action Text"
        onAction={() => {
          alert('action executed!');
        }}
        message="Lorem ipsum dolor sit amet consectetur adipisicing elit. Laboriosam perspiciatis non ipsa officia expedita magnam mollitia, excepturi iste eveniet qui nisi eum illum, quas voluptas, reprehenderit quam molestias cum quisquam!"
      />
    </StorySection>
  </>
);

AlertStory.storyName = 'with basic options';

export const AlertWithActionStory = (): React.ReactNode => (
  <>
    <StorySection title="Alert with text link">
      <Alert
        message={
          <span>
            Alert text that has a <a href="https://lyft.com">link</a>
          </span>
        }
      />
    </StorySection>
    <StorySection title="Alert with Action as button">
      <Alert
        message="Alert text that can be short"
        actionText="Action Text"
        onAction={() => {
          alert('action executed!');
        }}
      />
    </StorySection>
    <StorySection title="Alert with Action as link">
      <Alert
        message="Alert text that can be short"
        actionText="Action Text"
        actionHref="http://www.lyft.com"
      />
    </StorySection>
    <StorySection title="Alert with Action as custom link">
      <Alert
        message="Alert text that can be short"
        actionLink={
          <a className="test-action-link" href="http://testSite.com">
            Custom Link
          </a>
        }
      />
    </StorySection>
    <StorySection title="Alert with payload">
      <Alert
        message="Alert with payload"
        payload={{
          'Table name': 'coco.fact_rides',
          'Verity checks':
            '1 out of 4 checks failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
          'Failed DAGs':
            '1 out of 4 DAGs failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
          'Root cause':
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod',
          Estimate: 'Target fix by MM/DD/YYYY 00:00',
        }}
      />
    </StorySection>
  </>
);

AlertWithActionStory.storyName = 'with different types of actions';

export const AlertWithSeverityStory = (): React.ReactNode => (
  <>
    <StorySection title="Alert with info severity">
      <Alert
        severity={NoticeSeverity.INFO}
        message={
          <span>
            Info alert text that has a <a href="https://lyft.com">link</a>
          </span>
        }
      />
    </StorySection>
    <StorySection title="Alert with warning severity">
      <Alert
        severity={NoticeSeverity.WARNING}
        message={
          <span>
            Warning alert text that has a <a href="https://lyft.com">link</a>
          </span>
        }
      />
    </StorySection>
    <StorySection title="Alert with alert severity">
      <Alert
        severity={NoticeSeverity.ALERT}
        message={
          <span>
            Alert alert text that has a <a href="https://lyft.com">link</a>
          </span>
        }
      />
    </StorySection>
  </>
);

AlertWithSeverityStory.storyName = 'with different severities';

const list = [
  { severity: NoticeSeverity.INFO, messageHtml: 'First alert of the stack' },
  {
    severity: NoticeSeverity.WARNING,
    messageHtml: 'Second alert of the stack',
  },
  { severity: NoticeSeverity.ALERT, messageHtml: 'Third alert of the stack' },
];

export const AlertListStory = (): React.ReactNode => (
  <>
    <StorySection title="Alert List">
      <AlertList notices={list} />
    </StorySection>
  </>
);

AlertListStory.storyName = 'with AlertList';

export default {
  title: 'Components/Alert',
  component: Alert,
  decorators: [],
} as Meta;
