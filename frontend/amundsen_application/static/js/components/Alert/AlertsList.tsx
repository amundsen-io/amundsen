// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { NoticeType } from 'config/config-types';
import { Alert } from './Alert';

export interface AlertsListProps {
  notices: NoticeType[];
}

export const AlertsList: React.FC<AlertsListProps> = ({ notices }) => {
  if (!notices.length) {
    return null;
  }

  return (
    <div className="alerts-container">
      {notices.map((notice, idx) => (
        <Alert
          key={idx}
          message={notice.messageHtml}
          severity={notice.severity}
          payload={notice.payload}
        />
      ))}
    </div>
  );
};
