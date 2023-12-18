// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

import StorySection from '../StorySection';
import EditableSelect, {
  ComponentProps,
  DispatchFromProps,
  StateFromProps,
  SelectOption,
  SelectOptionAction
} from '.';

export default {
  title: 'Components/EditableSelect'
};

const dailyOption: SelectOption = {
  option: 'daily',
  action: SelectOptionAction.UPDATE
};
const weeklyOption: SelectOption = {
  option: 'weekly',
  action: SelectOptionAction.UPDATE
};
const monthlyOption: SelectOption = {
  option: 'monthly',
  action: SelectOptionAction.UPDATE
};
const annuallyOption: SelectOption = {
  option: 'annually',
  action: SelectOptionAction.UPDATE
};

export const SelectBox = () => (
  <>
    <StorySection title="with default Weekly">
      <EditableSelect value={'weekly'}
                      options={[dailyOption, weeklyOption, monthlyOption, annuallyOption]}
                      defaultOption='weekly'
                      editable={true} />
    </StorySection>
    <StorySection title="with no value specified">
      <EditableSelect options={[dailyOption, weeklyOption, monthlyOption, annuallyOption]}
                      editable={true} />
    </StorySection>
    <StorySection title="not editable">
      <EditableSelect value={'weekly'}
                      options={[dailyOption, weeklyOption, monthlyOption, annuallyOption]}
                      editable={false} />
    </StorySection>
  </>
);

SelectBox.storyName = 'Select Box';