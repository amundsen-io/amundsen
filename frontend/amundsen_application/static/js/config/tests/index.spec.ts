
import AppConfig from 'config/config';
import * as ConfigUtils from 'config/config-utils';

describe('feedbackEnabled', () => {
  it('returns whether or not the feaadback feature is enabled', () => {
    expect(ConfigUtils.feedbackEnabled()).toBe(AppConfig.mailClientFeatures.feedbackEnabled);
  });
});

describe('notificationsEnabled', () => {
  it('returns whether or not the notifications feature is enabled', () => {
    expect(ConfigUtils.notificationsEnabled()).toBe(AppConfig.mailClientFeatures.notificationsEnabled);
  });
});
