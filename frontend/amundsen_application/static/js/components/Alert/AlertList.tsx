// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { NoticeSeverity, NoticeType } from 'config/config-types';
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
  notices.reduce((accum, notice: NoticeType) => {
    if (notice) {
      const { messageHtml, severity, payload } = notice;

      if (typeof messageHtml !== 'function') {
        if (payload) {
          accum[messageHtml] ??= {};
          accum[messageHtml][severity] ??= {
            payload: { descriptions: [] },
          };
          accum[messageHtml][severity].payload.descriptions.push(payload);
        } else {
          accum[messageHtml] = {
            [severity]: { ...notice },
          };
        }
      }
    }

    return accum;
  }, {});

export const AlertList: React.FC<AlertListProps> = ({ notices }) => {
  if (!notices.length) {
    return null;
  }

  const aggregated = aggregateNotices(notices);
  const NoticeSeverityValues = Object.values(NoticeSeverity);

  return (
    <div className="alert-list">
      {Object.keys(aggregated).map((notice, idx) =>
        Object.keys(aggregated[notice])
          .sort(
            (a: NoticeSeverity, b: NoticeSeverity) =>
              NoticeSeverityValues.indexOf(a) - NoticeSeverityValues.indexOf(b)
          )
          .map((severity) => (
            <Alert
              key={idx}
              message={notice}
              severity={severity as NoticeSeverity}
              payload={aggregated[notice][severity].payload}
            />
          ))
      )}
    </div>
  );
};
