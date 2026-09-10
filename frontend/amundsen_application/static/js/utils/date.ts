import * as Moment from 'moment-timezone';

import { getDateConfiguration } from 'config/config-utils';

const timezone = Moment.tz.guess();

interface TimestampDateConfig {
  timestamp: number;
}

interface EpochDateConfig {
  epochTimestamp: number;
}

interface StringDateConfig {
  dateString: string;
  dateStringFormat: string;
}

type DateConfig = TimestampDateConfig | EpochDateConfig | StringDateConfig;

// This function is only exported for testing
export function getMomentDate(config: DateConfig): Moment.Moment {
  let moment;
  const { timestamp } = config as TimestampDateConfig;
  const { epochTimestamp } = config as EpochDateConfig;
  const { dateString, dateStringFormat } = config as StringDateConfig;

  if (timestamp !== undefined) {
    moment = Moment(timestamp);
  } else if (epochTimestamp !== undefined) {
    moment = Moment(epochTimestamp * 1000);
  } else if (dateString && dateStringFormat) {
    moment = Moment(dateString, dateStringFormat);
  } else {
    throw new Error('Cannot format date with invalid DateConfig object.');
  }

  return moment.tz(timezone);
}

export function formatDate(config: DateConfig) {
  const date = getMomentDate(config);
  const { default: defaultValue } = getDateConfiguration();

  return date.format(defaultValue);
}

export function formatDateTimeShort(config: DateConfig) {
  const date = getMomentDate(config);
  const { dateTimeShort } = getDateConfiguration();

  return date.format(dateTimeShort);
}

export function formatDateTimeLong(config: DateConfig) {
  const date = getMomentDate(config);
  const { dateTimeLong } = getDateConfiguration();

  return date.format(dateTimeLong);
}
