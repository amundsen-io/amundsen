import { SendingState } from '../../components/common/Feedback/types';

/* SubmitFeedback */
export enum SubmitFeedback {
  ACTION = 'amundsen/feedback/SUBMIT_FEEDBACK',
  SUCCESS = 'amundsen/feedback/SUBMIT_FEEDBACK_SUCCESS',
  FAILURE = 'amundsen/feedback/SUBMIT_FEEDBACK_FAILURE',
}

export interface SubmitFeedbackRequest {
  type: SubmitFeedback.ACTION;
  data: FormData;
}

interface SubmitFeedbackResponse {
  type: SubmitFeedback.SUCCESS | SubmitFeedback.FAILURE;
  payload?: FeedbackReducerState;
}

export function submitFeedback(formData): SubmitFeedbackRequest {
  return {
    data: formData,
    type: SubmitFeedback.ACTION,
  };
}

type SubmitFeedbackAction = SubmitFeedbackRequest | SubmitFeedbackResponse;
/* end SubmitFeedback */


/* ResetFeedback */
export enum ResetFeedback {
  ACTION = 'amundsen/feedback/RESET_FEEDBACK',
}

export interface ResetFeedbackAction {
  type: ResetFeedback.ACTION;
}

export function resetFeedback(): ResetFeedbackAction {
  return {
    type: ResetFeedback.ACTION,
  };
}

/* end ResetFeedback */

export type FeedbackReducerAction = SubmitFeedbackAction | ResetFeedbackAction;

export interface FeedbackReducerState {
  sendState: SendingState;
}

const initialState: FeedbackReducerState = {
  sendState: SendingState.IDLE
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
