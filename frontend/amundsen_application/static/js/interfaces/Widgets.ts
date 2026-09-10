// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

export interface Widget {
  name: string;
  options: {
    path: string;
    additionalProps?: object;
  };
}
