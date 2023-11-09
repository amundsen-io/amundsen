
export interface GPTMessage {
  content: string;
  role: string;
}

export interface GPTResponse {
  finish_reason: string;
  message: GPTMessage;
}

export interface GPTResponseParams {
  prompt: string;
}
