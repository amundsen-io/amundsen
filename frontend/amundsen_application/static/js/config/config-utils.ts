import AppConfig from 'config/config';
import { BadgeStyleConfig, BadgeStyle } from 'config/config-types';

export const DEFAULT_DATABASE_ICON_CLASS = 'icon-database icon-color';

/**
 * Returns the database display name for a given database id.
 * If a configuration or display name does not exist for the give id, the id
 * is returned.
 */
export function getDatabaseDisplayName(databaseId: string): string {
  const databaseConfig = AppConfig.resourceConfig.datasets[databaseId];
  if (!databaseConfig || !databaseConfig.displayName) {
    return databaseId;
  }

  return databaseConfig.displayName;
}

/**
 * Returns an icon class for a given database id, which should be a value
 * defined in `static/css/_icons.scss`.
 * If a configuration or icon class does not exist for the give id, the default
 * database icon class is returned.
 */
export function getDatabaseIconClass(databaseId: string): string {
  const databaseConfig = AppConfig.resourceConfig.datasets[databaseId];
  if (!databaseConfig || !databaseConfig.iconClass) {
    return DEFAULT_DATABASE_ICON_CLASS;
  }

  return databaseConfig.iconClass;
}

/**
 * Given a badge name, this will return a badge style and a display name.
 * If these are not specified by config, it will default to some simple rules:
 * use BadgeStyle.DEFAULT and replace '-' and '_' with spaces for display name.
 */
export function getBadgeConfig(badgeName: string): BadgeStyleConfig {
  const config = AppConfig.badges[badgeName] || {};

  return {
    style: BadgeStyle.DEFAULT,
    displayName: badgeName.replace(/[-_]/g, ' '),
    ...config,
  };
}

/**
 * Returns whether or not feedback features should be enabled
 */
export function feedbackEnabled(): boolean {
  return AppConfig.mailClientFeatures.feedbackEnabled;
}

/**
 * Returns whether or not user features should be shown
 */
export function indexUsersEnabled(): boolean {
  return AppConfig.indexUsers.enabled;
}

/**
 * Returns whether or not notification features should be enabled
 */
export function notificationsEnabled(): boolean {
  return AppConfig.mailClientFeatures.notificationsEnabled;
}

/**
 * Returns whether or not to show all tags
 */
export function showAllTags(): boolean {
  return AppConfig.browse.showAllTags;
}

/**
 * Returns a list of curated tag names
 */
export function getCuratedTags(): string[] {
  return AppConfig.browse.curatedTags;
}
