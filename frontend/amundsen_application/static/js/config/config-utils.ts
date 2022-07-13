import AppConfig from 'config/config';
import { BadgeStyle, BadgeStyleConfig } from 'config/config-types';
import { convertText, CaseType } from 'utils/textUtils';

import { TableMetadata } from 'interfaces/TableMetadata';
import { ResourceType } from '../interfaces';
import {
  AnalyticsConfig,
  FilterConfig,
  LinkConfig,
  NoticeType,
  TourConfig,
} from './config-types';

export const DEFAULT_DATABASE_ICON_CLASS = 'icon-database icon-color';
export const DEFAULT_DASHBOARD_ICON_CLASS = 'icon-dashboard icon-color';
const WILDCARD_SIGN = '*';
const RESOURCE_SEPARATOR = '.';
const ANNOUNCEMENTS_LINK_LABEL = 'Announcements';
const hasWildcard = (n) => n.indexOf(WILDCARD_SIGN) > -1;
const withComputedMessage = (notice: NoticeType, resourceName) => {
  if (typeof notice.messageHtml === 'function') {
    notice.messageHtml = notice.messageHtml(resourceName);
  }
  return notice;
};
const resourceMatches = (key: string, resource: string) => {
  if (key === resource || key === WILDCARD_SIGN) {
    return true;
  }
  if (key.includes(WILDCARD_SIGN)) {
    const wildcardIndex = key.indexOf(WILDCARD_SIGN);
    const inverseWildcardIndex = -1 * (key.length - wildcardIndex - 1);
    if (
      key.slice(0, wildcardIndex) === resource.slice(0, wildcardIndex) &&
      (wildcardIndex === key.length - 1 ||
        key.slice(inverseWildcardIndex) ===
          resource.slice(inverseWildcardIndex))
    ) {
      return true;
    }
  }
  return false;
};

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
    if (resource === ResourceType.feature) {
      return DEFAULT_DATABASE_ICON_CLASS;
    }
    return '';
  }

  return config.supportedSources[sourceId].iconClass;
}

/**
 * Returns notices for the given resource name if present
 */
export function getResourceNotices(
  resourceType: ResourceType,
  resourceName: string
): NoticeType | false {
  const { notices } = AppConfig.resourceConfig[resourceType];

  if (notices && notices[resourceName]) {
    const thisNotice = notices[resourceName];

    return withComputedMessage(thisNotice, resourceName);
  }

  const wildcardNoticesKeys = Object.keys(notices).filter(hasWildcard);
  if (wildcardNoticesKeys.length) {
    const wildcardNoticesArray = new Array(1);
    let hasNotice: boolean = false;

    wildcardNoticesKeys.forEach((key) => {
      const decomposedKey = key.split(RESOURCE_SEPARATOR);
      const decomposedResource = resourceName.split(RESOURCE_SEPARATOR);

      for (let i = 0; i < decomposedKey.length; i++) {
        if (resourceMatches(decomposedKey[i], decomposedResource[i])) {
          if (i === decomposedKey.length - 1) {
            wildcardNoticesArray[0] = notices[key];
            hasNotice = true;
          }
          continue;
        }
        break;
      }
    });
    if (hasNotice) {
      const [noticeFromWildcard] = wildcardNoticesArray;
      return withComputedMessage(noticeFromWildcard, resourceName);
    }
  }

  return false;
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
): FilterConfig | undefined {
  return AppConfig.resourceConfig[resourceType].filterCategories;
}

/**
 * Returns AnalyticsConfig.
 */
export function getAnalyticsConfig(): AnalyticsConfig {
  return AppConfig.analytics;
}

/**
 * Returns the stat type name for the unique value stat type
 * @returns string or undefined
 */
export function getUniqueValueStatTypeName(): string | undefined {
  return AppConfig.resourceConfig[ResourceType.table].stats
    ?.uniqueValueTypeName;
}

/*
 * Given a badge name, this will return a badge style and a display name.
 * If these are not specified by config, it will default to some simple rules:
 * use BadgeStyle.DEFAULT and badge name as display name.
 */
export function getBadgeConfig(badgeName: string): BadgeStyleConfig {
  const config: object = AppConfig.badges[badgeName] || {};

  return {
    style: BadgeStyle.DEFAULT,
    displayName: convertText(badgeName, CaseType.TITLE_CASE),
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
 * Returns whether or not ML features should be shown
 */
export function indexFeaturesEnabled(): boolean {
  return AppConfig.indexFeatures.enabled;
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
 * Returns the string that will prepopulate the issue description
 * text field with a template to suggest more detailed information
 * to be provided by the user when an issue is reported
 */
export function getIssueDescriptionTemplate(): string | undefined {
  return AppConfig.issueTracking.issueDescriptionTemplate;
}

/**
 * Returns whether users are able to override the default project in which to create the issue
 */
export function issueTrackingProjectSelectionEnabled(): boolean {
  const config = AppConfig.issueTracking.projectSelection;
  return config ? config.enabled : false;
}

/**
 * Returns the title for the selection field that allows more specificity in what you ask the user to enter
 */
export function getProjectSelectionTitle(): string {
  const config = AppConfig.issueTracking.projectSelection;
  return config ? config.title : '';
}

/**
 * Returns the hint to show the user what type of value is expected, such as the name of the default project
 */
export function getProjectSelectionHint(): string | undefined {
  const config = AppConfig.issueTracking.projectSelection;
  return config ? config.inputHint : '';
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
 * Returns a list of table sort options
 */
export function getTableSortCriterias() {
  const config = AppConfig.resourceConfig[ResourceType.table];

  if (config && config.sortCriterias) {
    return config.sortCriterias;
  }

  return {};
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

/**
 * Returns the display name for a given description source id for a given resource type.
 * If a configuration or display name does not exist for the given description source id, the id
 * is returned.
 */
export function getDescriptionSourceDisplayName(sourceId: string): string {
  const config = AppConfig.resourceConfig[ResourceType.table];
  if (
    config &&
    config.supportedDescriptionSources &&
    config.supportedDescriptionSources[sourceId] &&
    config.supportedDescriptionSources[sourceId].displayName
  ) {
    return config.supportedDescriptionSources[sourceId].displayName;
  }

  return sourceId;
}

/**
 * Returns the icon path for a given description source id for a given resource type.
 * If a configuration does not exist for the given description source id, empty string
 * is returned.
 */
export function getDescriptionSourceIconPath(sourceId: string): string {
  const config = AppConfig.resourceConfig[ResourceType.table];
  if (
    config &&
    config.supportedDescriptionSources &&
    config.supportedDescriptionSources[sourceId] &&
    config.supportedDescriptionSources[sourceId].iconPath
  ) {
    return config.supportedDescriptionSources[sourceId].iconPath;
  }

  return '';
}

/**
 * Returns the desired number format in which we want to format any number
 * Used for formatting column stats
 * If a configuration does not exist, None is returned
 */
export function getNumberFormat() {
  return AppConfig.numberFormat;
}

/**
 * Returns documentTitle.
 */
export function getDocumentTitle(): string {
  return AppConfig.documentTitle;
}

/**
 * Returns logoTitle.
 */
export function getLogoTitle(): string {
  return AppConfig.logoTitle;
}

/**
 * Returns whether the in-app table lineage list is enabled.
 */
export function isFeatureListLineageEnabled() {
  return AppConfig.featureLineage.inAppListEnabled;
}

/**
 * Returns whether the in-app table lineage list is enabled.
 */
export function isTableListLineageEnabled() {
  return AppConfig.tableLineage.inAppListEnabled;
}

/**
 * Returns whether the in-app column list lineage is enabled.
 */
export function isColumnListLineageEnabled() {
  return AppConfig.columnLineage.inAppListEnabled;
}

/**
 * Returns whether the in-app table lineage page is enabled.
 */
export function isTableLineagePageEnabled() {
  return AppConfig.tableLineage.inAppPageEnabled;
}

/**
 * Returns whether the in-app column lineage page is enabled.
 */
export function isColumnLineagePageEnabled() {
  return AppConfig.columnLineage.inAppPageEnabled;
}

/**
 * Returns the lineage link for a given column
 */
export function getColumnLineageLink(
  tableData: TableMetadata,
  columnName: string
) {
  return AppConfig.columnLineage.urlGenerator(
    tableData.database,
    tableData.cluster,
    tableData.schema,
    tableData.name,
    columnName
  );
}

/**
 * Returns whether table data quality checks are enabled
 */
export function isTableQualityCheckEnabled() {
  return AppConfig.tableQualityChecks.isEnabled;
}

/**
 * Returns whether Available badges section should be shown in Home Page
 */
export function isShowBadgesInHomeEnabled() {
  return AppConfig.browse.showBadgesInHome;
}

/**
 * Returns the maximum number of columns allowed to show nested columns
 */
export function getMaxNestedColumns() {
  return AppConfig.nestedColumns.maxNestedColumns;
}

/**
 * Returns the configuration for the Product Tour
 */
export function getProductToursFor(
  path: string
): { result: TourConfig[] | null; tourPath: string } {
  let result: TourConfig[] | null = null;
  let tourPath: string = '';

  if (AppConfig.productTour[path] && AppConfig.productTour[path].length) {
    result = AppConfig.productTour[path];
    tourPath = path;
  }

  const wildcardPathKeys = Object.keys(AppConfig.productTour).filter(
    hasWildcard
  );
  if (wildcardPathKeys.length) {
    wildcardPathKeys.forEach((key) => {
      const decomposedKey = key.substring(0, key.length - 1);

      if (path.startsWith(decomposedKey)) {
        result = AppConfig.productTour[key];
        tourPath = key;
      }
    });
  }

  return { result, tourPath };
}

export function searchHighlightingEnabled(resource: ResourceType): boolean {
  return AppConfig.resourceConfig[resource].searchHighlight.enableHighlight;
}

/**
 * Returns the search results pagination configuration
 */
export function getSearchResultsPerPage(): number {
  return AppConfig.searchPagination.resultsPerPage;
}
