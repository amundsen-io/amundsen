import axios, { AxiosResponse, AxiosError } from 'axios';

import { SubmitFeedbackRequest } from '../types';

export function feedbackSubmitFeedback(action: SubmitFeedbackRequest) {
  return axios({
    data: action.data,
    method: 'post',
    url: '/api/mail/v0/feedback',
    timeout: 5000,
    headers: {'Content-Type': 'multipart/form-data' }
  })
  .then((response: AxiosResponse<any>) => {
    return response;
  })
  .catch((error: AxiosError) => {
    return error;
  });
}
