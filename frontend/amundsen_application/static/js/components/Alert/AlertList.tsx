// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { NoticeType } from 'config/config-types';
import { Alert } from './Alert';

export interface AlertListProps {
  notices: NoticeType[];
}

export interface AggregatedAlertListProps {
  notices: {
    [key: string]: NoticeType;
  };
}

const aggregateNotices = (notices) =>
  notices.reduce((accum, notice: any) => {
    if (notice) {
      const { messageHtml, severity, payload } = notice;

      if (payload) {
        accum[messageHtml] ??= {
          severity,
          payload: { descriptions: [] },
        };
        accum[messageHtml].payload.descriptions.push(payload);
      } else {
        accum[messageHtml] = { ...notice };
      }
    }

    return accum;
  }, {});

export const AlertList: React.FC<AlertListProps> = ({ notices }) => {
  if (!notices.length) {
    return null;
  }

  const aggregated = aggregateNotices(notices);

  return (
    <div className="alert-list">
      {Object.keys(aggregated).map((notice, idx) => (
        <Alert
          key={idx}
          message={notice}
          severity={aggregated[notice].severity}
          payload={aggregated[notice].payload}
        />
      ))}
    </div>
  );
};
