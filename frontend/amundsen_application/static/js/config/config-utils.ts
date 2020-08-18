import AppConfig from 'config/config';
import { BadgeStyleConfig, BadgeStyle } from 'config/config-types';
import { TableMetadata } from 'interfaces/TableMetadata';

import { FilterConfig, LinkConfig } from './config-types';

import { ResourceType } from '../interfaces';

export const DEFAULT_DATABASE_ICON_CLASS = 'icon-database icon-color';
export const DEFAULT_DASHBOARD_ICON_CLASS = 'icon-dashboard icon-color';
const ANNOUNCEMENTS_LINK_LABEL = 'Announcements';

/**
 * Returns the display name for a given source id for a given resource type.
 * If a configuration or display name does not exist for the given id, the id
 * is returned.
 */
export function getSourceDisplayName(
  sourceId: string,
  resource: ResourceType
): string {
  const config = AppConfig.resourceConfig[resource];
  if (
    !config ||
    !config.supportedSources ||
    !config.supportedSources[sourceId]
  ) {
    return sourceId;
  }

  return config.supportedSources[sourceId].displayName;
}

/**
 * Returns an icon class for a given source id for a given resource type,
 * which should be a value defined in `static/css/_icons.scss`.
 * If a configuration or icon class does not exist for the given id, the default
 * icon class for the given resource type is returned.
 */
export function getSourceIconClass(
  sourceId: string,
  resource: ResourceType
): string {
  const config = AppConfig.resourceConfig[resource];
  if (
    !config ||
    !config.supportedSources ||
    !config.supportedSources[sourceId]
  ) {
    if (resource === ResourceType.dashboard) {
      return DEFAULT_DASHBOARD_ICON_CLASS;
    }
    if (resource === ResourceType.table) {
      return DEFAULT_DATABASE_ICON_CLASS;
    }
    return '';
  }

  return config.supportedSources[sourceId].iconClass;
}

/**
 * Returns the displayName for the given resourceType
 */
export function getDisplayNameByResource(resourceType: ResourceType): string {
  return AppConfig.resourceConfig[resourceType].displayName;
}

/**
 * Returns the filterCategories for the given resourceType
 */
export function getFilterConfigByResource(
  resourceType: ResourceType
): FilterConfig {
  return AppConfig.resourceConfig[resourceType].filterCategories;
}

/*
 * Given a badge name, this will return a badge style and a display name.
 * If these are not specified by config, it will default to some simple rules:
 * use BadgeStyle.DEFAULT and badge name as display name.
 */
export function getBadgeConfig(badgeName: string): BadgeStyleConfig {
  const config = AppConfig.badges[badgeName] || {};

  return {
    style: BadgeStyle.DEFAULT,
    displayName: badgeName,
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
 * Returns whether or not feedback features should be enabled
 */
export function announcementsEnabled(): boolean {
  return AppConfig.announcements.enabled;
}

/**
 * Returns whether or not dashboard features should be shown
 */
export function indexDashboardsEnabled(): boolean {
  return AppConfig.indexDashboards.enabled;
}

/**
 * Returns whether or not user features should be shown
 */
export function indexUsersEnabled(): boolean {
  return AppConfig.indexUsers.enabled;
}

/**
 * Returns whether or not the issue tracking feature should be shown
 */
export function issueTrackingEnabled(): boolean {
  return AppConfig.issueTracking.enabled;
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

/**
 * Checks if nav links are active
 */
const isNavLinkActive = (link: LinkConfig): boolean => {
  if (!announcementsEnabled()) {
    return link.label !== ANNOUNCEMENTS_LINK_LABEL;
  }

  return true;
};

/*
 * Returns the updated list of navigation links given the other
 * configuration options state
 */
export function getNavLinks(): LinkConfig[] {
  return AppConfig.navLinks.filter(isNavLinkActive);
}

/**
 * Returns whether to enable the table `explore` feature
 */
export function exploreEnabled(): boolean {
  return AppConfig.tableProfile.isExploreEnabled;
}

/**
 * Generates the explore URL from a table metadata object
 *
 * @param tableData
 */
export function generateExploreUrl(tableData: TableMetadata): string {
  const { partition } = tableData;

  if (partition.is_partitioned) {
    return AppConfig.tableProfile.exploreUrlGenerator(
      tableData.database,
      tableData.cluster,
      tableData.schema,
      tableData.name,
      partition.key,
      partition.value
    );
  }
  return AppConfig.tableProfile.exploreUrlGenerator(
    tableData.database,
    tableData.cluster,
    tableData.schema,
    tableData.name
  );
}

/**
 * Gets the max length for items with a configurable max length.
 * Currently only applied to `editableText`, but method can be extended for future cases
 */
export function getMaxLength(key: string) {
  return AppConfig.editableText[key];
}
