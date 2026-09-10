// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

export interface AnalyticsEvent {
  name: string;
  payload: { [prop: string]: unknown };
}
