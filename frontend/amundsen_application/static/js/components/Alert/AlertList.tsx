// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { NoticeType } from 'config/config-types';
import { Alert } from './Alert';

export interface AlertListProps {
  notices: NoticeType[];
}

export const AlertList: React.FC<AlertListProps> = ({ notices }) => {
  if (!notices.length) {
    return null;
  }

  return (
    <div className="alert-list">
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
