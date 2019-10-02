import { NotificationType, SendNotificationOptions } from 'interfaces'

export enum SubmitNotification {
  REQUEST = 'amundsen/notification/SUBMIT_NOTIFICATION_REQUEST',
  SUCCESS = 'amundsen/notification/SUBMIT_NOTIFICATION_SUCCESS',
  FAILURE = 'amundsen/notification/SUBMIT_NOTIFICATION_FAILURE',
};

export interface SubmitNotificationRequest {
  type: SubmitNotification.REQUEST;
  payload: {
    recipients: Array<string>,
    sender: string,
    notificationType: NotificationType,
    options?: SendNotificationOptions
  };
};
export interface SubmitNotificationResponse {
  type: SubmitNotification.SUCCESS | SubmitNotification.FAILURE;
};

export enum ToggleRequest {
  OPEN = 'open',
  CLOSE = 'close',
};

export interface ToggleRequestAction {
  type: ToggleRequest.OPEN | ToggleRequest.CLOSE;
};
