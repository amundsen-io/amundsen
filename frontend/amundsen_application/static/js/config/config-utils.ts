import AppConfig from 'config/config';

export function feedbackEnabled(): boolean {
  return AppConfig.mailClientFeatures.feedbackEnabled;
}

export function notificationsEnabled(): boolean {
  return AppConfig.mailClientFeatures.notificationsEnabled;
}
