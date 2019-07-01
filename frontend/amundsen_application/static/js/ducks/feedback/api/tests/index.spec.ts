import axios from 'axios';

import { feedbackSubmit } from '../v0';

jest.mock('axios');

describe('feedbackSubmit', () => {
  let formData: FormData;
  beforeAll(() => {
    formData = new FormData();
    feedbackSubmit(formData);
  });

  it('calls axios with expected payload', () => {
    expect(axios).toHaveBeenCalledWith({
      data: formData,
      method: 'post',
      url: '/api/mail/v0/feedback',
      timeout: 5000,
      headers: {'Content-Type': 'multipart/form-data' }
    })
  });
});
