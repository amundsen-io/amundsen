// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { GPTResponse } from 'interfaces/AI';
import {
  GetGPTResponse,
  GetGPTResponseRequest,
  GetGPTResponseResponse
} from './types';


export const initialGPTResponseState =
    {
      finish_reason: '',
      message: {
        content: '',
        role: ''
      }
    }

export const initialState: GPTResponseReducerState = {
  isLoading: false,
  gptResponse: initialGPTResponseState
};

/* ACTIONS */
export function getGPTResponse(
  prompt: string,
  onSuccess?: (gtpRespnse: GetGPTResponseResponse) => any,
  onFailure?: (gtpRespnse: GetGPTResponseResponse) => any): GetGPTResponseRequest {
  return {
    payload: {
      prompt,
      onSuccess,
      onFailure,
    },
    type: GetGPTResponse.REQUEST
  };
}
export function getGPTResponseFailure(): GetGPTResponseResponse {
  return {
    type: GetGPTResponse.FAILURE,
    payload: { gptResponse: initialGPTResponseState }
  };
}
export function getGPTResponseSuccess(gptResponse: GPTResponse): GetGPTResponseResponse {
  return {
    type: GetGPTResponse.SUCCESS,
    payload: { gptResponse }
  };
}

/* REDUCER */
export interface GPTResponseReducerState {
  isLoading: boolean;
  gptResponse: GPTResponse;
}

export default function reducer(
  state: GPTResponseReducerState = initialState,
  action
): GPTResponseReducerState {
  switch (action.type) {
    case GetGPTResponse.REQUEST:
      return {
        isLoading: true,
        gptResponse: state.gptResponse
      };
    case GetGPTResponse.FAILURE:
      return initialState;
    case GetGPTResponse.SUCCESS:
      return {
        isLoading: false,
        gptResponse: (<GetGPTResponseResponse>action).payload.gptResponse
      };
    default:
      return state;
  }
}
