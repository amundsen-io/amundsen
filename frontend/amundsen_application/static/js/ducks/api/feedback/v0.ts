import axios from 'axios';

import { SubmitFeedbackRequest } from '../../feedback/reducer';

export function feedbackSubmitFeedback(action: SubmitFeedbackRequest) {
  const { data } = action;

  return axios({
      data,
      method: 'post',
      url: '/api/mail/feedback',
      timeout: 5000,
      headers: {'Content-Type': 'multipart/form-data' }
    })
    .then((response) => {
      return response
    })
    .catch((error) => {
      return error
    });
}
