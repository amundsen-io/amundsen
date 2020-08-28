import React from 'react';
import { storiesOf } from '@storybook/react';

import { BadgeStyle } from 'config/config-types';
import StorySection from '../StorySection';
import Flag, { CaseType } from '.';

const stories = storiesOf('Components/Flags', module);

stories.add('Flags', () => (
  <>
    <StorySection title="Lower Case Flag">
      <Flag caseType={CaseType.LOWER_CASE} text="Test Flag" />
    </StorySection>
    <StorySection title="Upper Case Flag">
      <Flag caseType={CaseType.UPPER_CASE} text="Test Flag" />
    </StorySection>
    <StorySection title="Sentence Case Flag">
      <Flag caseType={CaseType.SENTENCE_CASE} text="Test Flag" />
    </StorySection>
    <StorySection title="Default Style Flag">
      <Flag
        caseType={CaseType.SENTENCE_CASE}
        text="Test Flag"
        labelStyle={BadgeStyle.DEFAULT}
      />
    </StorySection>
    <StorySection title="Primary Style Flag">
      <Flag
        caseType={CaseType.SENTENCE_CASE}
        text="Test Flag"
        labelStyle={BadgeStyle.PRIMARY}
      />
    </StorySection>
    <StorySection title="Informational Style Flag">
      <Flag
        caseType={CaseType.SENTENCE_CASE}
        text="Test Flag"
        labelStyle={BadgeStyle.INFO}
      />
    </StorySection>
    <StorySection title="Success Style Flag">
      <Flag
        caseType={CaseType.SENTENCE_CASE}
        text="Test Flag"
        labelStyle={BadgeStyle.SUCCESS}
      />
    </StorySection>
    <StorySection title="Warning Style Flag">
      <Flag
        caseType={CaseType.SENTENCE_CASE}
        text="Test Flag"
        labelStyle={BadgeStyle.WARNING}
      />
    </StorySection>
    <StorySection title="Danger Style Flag">
      <Flag
        caseType={CaseType.SENTENCE_CASE}
        text="Test Flag"
        labelStyle={BadgeStyle.DANGER}
      />
    </StorySection>
  </>
));
