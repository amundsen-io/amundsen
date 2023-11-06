import axios, { AxiosResponse } from 'axios';

import { GPTResponse } from 'interfaces';


export const API_PATH = '/api/ai/v0';

export type GPTResponseAPI = {
  msg: string;
  gptResponse: GPTResponse;
};

export function getGPTResponse(prompt: string) {
  return axios
  .get(`${API_PATH}/get_gpt_response?prompt=${encodeURIComponent(prompt)}`)
    .then((response: AxiosResponse<GPTResponseAPI>) =>
      response.data.gptResponse
    );
}