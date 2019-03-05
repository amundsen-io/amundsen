import { SendingState } from '../../components/common/Feedback/types';

import {
  ResetFeedback, ResetFeedbackRequest,
  SubmitFeedback, SubmitFeedbackRequest, SubmitFeedbackResponse,
} from './types';

export type SubmitFeedbackAction = SubmitFeedbackRequest | SubmitFeedbackResponse;
export type ResetFeedbackAction = ResetFeedbackRequest;

export type FeedbackReducerAction = SubmitFeedbackAction | ResetFeedbackAction;

export interface FeedbackReducerState {
  sendState: SendingState;
}

export function submitFeedback(formData: FormData): SubmitFeedbackRequest {
  return {
    data: formData,
    type: SubmitFeedback.ACTION,
  };
}

export function resetFeedback(): ResetFeedbackAction {
  return {
    type: ResetFeedback.ACTION,
  };
}

const initialState: FeedbackReducerState = {
  sendState: SendingState.IDLE,
};

export default function reducer(state: FeedbackReducerState = initialState, action: FeedbackReducerAction): FeedbackReducerState {
  switch (action.type) {
    case SubmitFeedback.ACTION:
      return { sendState: SendingState.WAITING };
    case SubmitFeedback.SUCCESS:
      return { sendState: SendingState.COMPLETE };
    case SubmitFeedback.FAILURE:
      alert('Your feedback was not submitted, please try again');
      return { sendState: SendingState.IDLE };
    case ResetFeedback.ACTION:
      return { sendState: SendingState.IDLE };
    default:
      return state;
  }
}
