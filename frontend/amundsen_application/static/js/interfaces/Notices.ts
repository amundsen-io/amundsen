// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { NoticeSeverity, NoticePayload } from '../config/config-types';

export interface DynamicResourceNotice {
  severity: NoticeSeverity;
  message: string;
  payload?: NoticePayload;
}
