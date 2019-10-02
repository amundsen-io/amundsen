import { NotificationType, SendNotificationOptions, SendingState } from 'interfaces'

import {
  SubmitNotification,
  SubmitNotificationRequest,
  SubmitNotificationResponse,
  ToggleRequest,
  ToggleRequestAction,
} from './types';

/* ACTIONS */
export function submitNotification(recipients: Array<string>, sender: string, notificationType: NotificationType, options?: SendNotificationOptions): SubmitNotificationRequest {
  return {
    payload: {
        recipients,
        sender,
        notificationType,
        options
    },
    type: SubmitNotification.REQUEST,
  };
};
export function submitNotificationFailure(): SubmitNotificationResponse {
  return {
    type: SubmitNotification.FAILURE,
  };
};
export function submitNotificationSuccess(): SubmitNotificationResponse {
  return {
    type: SubmitNotification.SUCCESS,
  };
};

export function closeRequestDescriptionDialog(): ToggleRequestAction {
  return {
    type: ToggleRequest.CLOSE,
  };
};

export function openRequestDescriptionDialog(): ToggleRequestAction {
  return {
    type: ToggleRequest.OPEN,
  }
}

/* REDUCER */
export interface NotificationReducerState {
  requestIsOpen: boolean,
  sendState: SendingState,
};

const initialState: NotificationReducerState = {
  requestIsOpen: false,
  sendState: SendingState.IDLE,
};

export default function reducer(state: NotificationReducerState = initialState, action): NotificationReducerState {
  switch (action.type) {
    case SubmitNotification.FAILURE:
      return {
        ...state,
        sendState: SendingState.ERROR,
      }
    case SubmitNotification.SUCCESS:
      return {
        ...state,
        sendState: SendingState.COMPLETE,
      }
    case SubmitNotification.REQUEST:
      return {
        requestIsOpen: false,
        sendState: SendingState.WAITING,
      }
    case ToggleRequest.CLOSE:
      return {
        requestIsOpen: false,
        sendState: SendingState.IDLE,
      }
    case ToggleRequest.OPEN:
      return {
        requestIsOpen: true,
        sendState: SendingState.IDLE,
      }
    default:
      return state;
  }
};
