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
export interface SubmitFeedbackResponse {
  type: SubmitFeedback.SUCCESS | SubmitFeedback.FAILURE;
}

/* ResetFeedback */
export enum ResetFeedback {
  ACTION = 'amundsen/feedback/RESET_FEEDBACK',
}
export interface ResetFeedbackRequest {
  type: ResetFeedback.ACTION;
}
