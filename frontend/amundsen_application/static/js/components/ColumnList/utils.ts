// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { formatDate } from 'utils/dateUtils';

export const getStatsInfoText = (startEpoch?: number, endEpoch?: number) => {
  const startDate = startEpoch
    ? formatDate({ epochTimestamp: startEpoch })
    : null;
  const endDate = endEpoch ? formatDate({ epochTimestamp: endEpoch }) : null;

  let infoText = 'Stats reflect data collected';

  if (startDate && endDate) {
    if (startDate === endDate) {
      infoText = `${infoText} on ${startDate} only. (daily partition)`;
    } else {
      infoText = `${infoText} between ${startDate} and ${endDate}.`;
    }
  } else {
    infoText = `${infoText} over a recent period of time.`;
  }

  return infoText;
};
