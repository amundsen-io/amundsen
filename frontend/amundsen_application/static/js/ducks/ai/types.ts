// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { GPTResponse } from 'interfaces';

export enum GetGPTResponse {
  REQUEST = 'amundsen/ai/GET_GPT_RESPONSE_REQUEST',
  SUCCESS = 'amundsen/ai/GET_GPT_RESPONSE_SUCCESS',
  FAILURE = 'amundsen/ai/GET_GPT_RESPONSE_FAILURE',
}
export interface GetGPTResponseRequest {
  type: GetGPTResponse.REQUEST;
  payload: {
    prompt: string;
  };
}
export interface GetGPTResponseResponse {
  type: GetGPTResponse.SUCCESS | GetGPTResponse.FAILURE;
  payload: {
    gptResponse: GPTResponse;
  };
}
