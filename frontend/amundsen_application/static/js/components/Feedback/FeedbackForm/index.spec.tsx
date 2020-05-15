import * as React from 'react';

import { shallow } from 'enzyme';

import LoadingSpinner from 'components/common/LoadingSpinner';
import { SendingState } from 'interfaces';
import FeedbackForm, { FeedbackFormProps } from '.';
import { RatingFeedbackForm } from './RatingFeedbackForm';

import {
  SUBMIT_FAILURE_MESSAGE,
  SUBMIT_SUCCESS_MESSAGE,
} from '../constants';

const mockFormData = { key1: 'val1', key2: 'val2' };
// @ts-ignore: How to mock FormData without TypeScript error?
global.FormData = () => (mockFormData);

describe('FeedbackForm', () => {
  const setup = (propOverrides?: Partial<FeedbackFormProps>) => {
    const props: FeedbackFormProps = {
      sendState: SendingState.IDLE,
      submitFeedback: jest.fn(),
      resetFeedback: jest.fn(),
      ...propOverrides
    };
    const wrapper = shallow<RatingFeedbackForm>(<RatingFeedbackForm {...props} />);
    return { props, wrapper };
  };

  describe('submitForm', () => {
    it('calls submitFeedback with formData', () => {
      const { props, wrapper } = setup();
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().submitForm({ preventDefault: jest.fn() });
      expect(props.submitFeedback).toHaveBeenCalledWith(mockFormData);
    });
  });

  describe('render', () => {
    it('calls renderCustom if sendState is not WAITING or COMPLETE', () => {
      const { props, wrapper } = setup();
      const renderCustomSpy = jest.spyOn(wrapper.instance(), 'renderCustom');
      wrapper.instance().render();
      expect(renderCustomSpy).toHaveBeenCalled();
    });

    it('renders LoadingSpinner if sendState is WAITING', () => {
      const { props, wrapper } = setup({sendState: SendingState.WAITING});
      expect(wrapper.find('LoadingSpinner').exists()).toBeTruthy();
    });

    it('renders confirmation status message if sendState is COMPLETE', () => {
      const { props, wrapper } = setup({sendState: SendingState.COMPLETE});
      expect(wrapper.find('div.status-message').text()).toEqual(SUBMIT_SUCCESS_MESSAGE);
    });

    it('renders failure status message if sendState is ERROR', () => {
      const { props, wrapper } = setup({sendState: SendingState.ERROR});
      expect(wrapper.find('div.status-message').text()).toEqual(SUBMIT_FAILURE_MESSAGE);
    });
  });
});
