import {
  FilterOperationType,
  FilterType,
  ResourceType,
  SortCriteria,
} from '../interfaces';

import { Widget } from '../interfaces/Widgets';

/**
 * AppConfig and AppConfigCustom should share the same definition, except each field in AppConfigCustom
 * is optional. If you choose to override one of the configs, you must provide the full type definition
 * for that section.
 */

export interface AppConfig {
  analytics: AnalyticsConfig;
  announcements: AnnoucementsFeaturesConfig;
  badges: BadgeConfig;
  browse: BrowseConfig;
  columnLineage: ColumnLineageConfig;
  date: DateFormatConfig;
  documentTitle: string;
  editableText: EditableTextConfig;
  featureLineage: FeatureLineageConfig;
  homePageWidgets: HomePageWidgetsConfig;
  indexDashboards: IndexDashboardsConfig;
  indexFeatures: IndexFeaturesConfig;
  indexUsers: IndexUsersConfig;
  issueTracking: IssueTrackingConfig;
  logoPath: string | null;
  logoTitle: string;
  mailClientFeatures: MailClientFeaturesConfig;
  navAppSuite: VisualLinkConfig[] | null;
  navLinks: LinkConfig[];
  navTheme: 'dark' | 'light';
  nestedColumns: NestedColumnConfig;
  numberFormat: NumberFormatConfig | null;
  productTour: ToursConfig;
  resourceConfig: ResourceConfig;
  searchPagination: SearchPagination;
  tableLineage: TableLineageConfig;
  tableProfile: TableProfileConfig;
  tableQualityChecks: TableQualityChecksConfig;
  userIdLabel: string /* Temporary configuration due to lacking string customization/translation support */;
}

/**
 * configExternal - If you choose to override one of the configs, you must provide the full type definition
 * for configExternal
 */

export interface AppConfigExternal {
  configExternal: AppConfig;
}

export interface AppConfigCustom {
  analytics?: AnalyticsConfig;
  badges?: BadgeConfig;
  browse?: BrowseConfig;
  date?: DateFormatConfig;
  editableText?: EditableTextConfig;
  indexDashboards?: IndexDashboardsConfig;
  indexUsers?: IndexUsersConfig;
  indexFeatures?: IndexFeaturesConfig;
  userIdLabel?: string /* Temporary configuration due to lacking string customization/translation support */;
  issueTracking?: IssueTrackingConfig;
  logoPath?: string;
  logoTitle?: string;
  documentTitle?: string;
  numberFormat?: NumberFormatConfig | null;
  mailClientFeatures?: MailClientFeaturesConfig;
  announcements?: AnnoucementsFeaturesConfig;
  navAppSuite?: VisualLinkConfig[];
  navLinks?: LinkConfig[];
  navTheme?: 'dark' | 'light';
  resourceConfig?: ResourceConfig;
  featureLineage?: FeatureLineageConfig;
  tableLineage?: TableLineageConfig;
  columnLineage?: ColumnLineageConfig;
  tableProfile?: TableProfileConfig;
  tableQualityChecks?: TableQualityChecksConfig;
  nestedColumns?: NestedColumnConfig;
  productTour?: ToursConfig;
  searchPagination?: SearchPagination;
  homePageWidgets?: HomePageWidgetsConfig;
}

/**
 * Enable search results highlighting of matching metadata for a resource
 */
export interface ResourceHighlightConfig {
  enableHighlight: boolean;
}

/**
 * AnalyticsConfig - Configure a single analytics destination
 *
 * plugins - array of AnalyticsPlugin functions (upstream doesn't expose this type, so any).
 */
export interface AnalyticsConfig {
  plugins: any[];
}

/**
 * BrowseConfig - Customize the 'browse' page.
 *
 * curatedTags - An array of tags to show in a separate section at the top.
 * showAllTags - Shows all tags when true, or only curated tags if false
 * showBadgesInHome - Shows all badges in the homepage when true
 * hideNonClickableBadges - Hides non-clickable badges in the homepage if true
 */
interface BrowseConfig {
  curatedTags: string[];
  showAllTags: boolean;
  showBadgesInHome: boolean;
  hideNonClickableBadges: boolean;
}

/**
 * The data shape of CheckboxFilterCategory.options
 *
 * displayName - The display name of the checkbox filter option
 * value - The value the option represents
 */
interface CheckboxFilterOptions {
  displayName?: string;
  value: string;
}

/**
 * Base interface for all possible FilterConfig objects
 *
 * categoryId - The filter category that this config represents, e.g. 'database' or 'badges'
 * displayName - The displayName for the filter category
 * allowableOperation - If this is not set, the default behavior will allow both AND and OR operations for filtering.
 *                      FilterOperationType.OR: a user can only select OR when entering multiple filter terms - this
 *                                              can be used for when a search result can contain only a single value
 *                                              of this filter category
 *                      FilterOperationType.AND: a user can only select AND when entering multiple filter terms
 * helpText - An option string of text that will render in the filter UI for the filter category
 * type - The FilterType for this filter category
 * defaultValue - if set the filter is applied to every search by default with the configured value
 */
interface BaseFilterCategory {
  categoryId: string;
  displayName: string;
  allowableOperation?: FilterOperationType;
  helpText?: string;
  type: FilterType;
  defaultValue?: string[];
}

/**
 * Interface for filter categories displayed as toggle
 */
interface ToggleFilterCategory extends BaseFilterCategory {
  type: FilterType.TOGGLE_FILTER;
}

/**
 * Interface for filter categories displayed as checkbox selection
 */
interface CheckboxFilterCategory extends BaseFilterCategory {
  type: FilterType.CHECKBOX_SELECT;
  options: CheckboxFilterOptions[];
}

/**
 * Interface for filter categories displayed as an input text box
 */
export interface InputFilterCategory extends BaseFilterCategory {
  type: FilterType.INPUT_SELECT;
}

/**
 * Configures filter categories for each resource
 */
export type FilterConfig = (
  | CheckboxFilterCategory
  | InputFilterCategory
  | ToggleFilterCategory
)[];

/**
 * Configures the UI for a given entity source
 */
type SourcesConfig = {
  [id: string]: {
    displayName?: string;
    iconClass?: string;
  };
};

/**
 * Configures the UI for a given table description source
 */
type DescriptionSourceConfig = {
  [id: string]: { displayName: string; iconPath: string };
};

/**
 * Shows criterias to sort tables
 */
type SortCriteriaConfig = {
  [key: string]: SortCriteria;
};

export enum NoticeSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ALERT = 'alert',
}

export type NoticePayload = Record<string, string>;

export interface NoticeType {
  severity: NoticeSeverity;
  messageHtml: string | ((resourceName: string) => string);
  payload?: NoticePayload;
}

/**
 * Stats configuration options
 *
 * uniqueValueTypeName - The stat type name for the unique value stat type
 * iconNotRequiredTypes - List of stat types where, if they are the only ones present,
 * the stats icon will not be displayed. This can be used for commonly occurring stats such as usage.
 */
type StatsConfig = {
  uniqueValueTypeName?: string;
  iconNotRequiredTypes?: string[];
};

/**
 * A list of notices where the key is the 'schema.name' of the table and the value
 * a Notice
 */
type NoticesConfigType = Record<string, NoticeType>;

/**
 * Base interface for all possible ResourceConfig objects
 *
 * displayName - The name displayed throughout the application to refer to this resource type
 * filterCategories - Optional configuration for any filters that can be applied to this resource
 */
interface BaseResourceConfig {
  displayName: string;
  filterCategories?: FilterConfig;
  supportedSources?: SourcesConfig;
  notices?: NoticesConfigType;
  hasDynamicNoticesEnabled?: boolean;
  searchHighlight?: ResourceHighlightConfig;
}

interface TableResourceConfig extends BaseResourceConfig {
  supportedDescriptionSources?: DescriptionSourceConfig;
  sortCriterias?: SortCriteriaConfig;
  stats?: StatsConfig;
}

export enum BadgeStyle {
  DANGER = 'negative',
  DEFAULT = 'neutral',
  INFO = 'info',
  PRIMARY = 'primary',
  SUCCESS = 'positive',
  WARNING = 'warning',
}

export interface BadgeStyleConfig {
  style: BadgeStyle;
  displayName?: string;
}

/**
 * BadgeConfig - Configure badge colors
 *
 * An object that maps badges to BadgeStyleConfigs
 */
interface BadgeConfig {
  [badge: string]: BadgeStyleConfig;
}

/**
 * DateConfig - Configure various date formats
 *
 */
export interface DateFormatConfig {
  default: string;
  dateTimeLong: string;
  dateTimeShort: string;
}

/** ResourceConfig - For customizing values related to how various resources
 *                   are displayed in the UI.
 *
 * A map of each resource type to its configuration
 */
interface ResourceConfig {
  [ResourceType.dashboard]: BaseResourceConfig;
  [ResourceType.table]: TableResourceConfig;
  [ResourceType.user]: BaseResourceConfig;
  [ResourceType.feature]: BaseResourceConfig;
}

/**
 * MailClientFeaturesConfig - Enable/disable UI features with a dependency on
 *                            configuring a custom mail client.
 *
 * feedbackEnabled - Enables the feedback feature UI
 * notificationsEnabled - Enables any UI related to sending notifications to users
 */
interface MailClientFeaturesConfig {
  feedbackEnabled: boolean;
  notificationsEnabled: boolean;
}

/**
 * AnnoucementsFeaturesConfig - Enable/disable UI features related to the announcements
 *
 * enabled - Enables the announcements feature
 */
interface AnnoucementsFeaturesConfig {
  enabled: boolean;
}

/**
 * TableProfileConfig - Customize the "Table Profile" section of the "Table Details" page.
 *
 * isBeta - Adds a "beta" tag to the "Table Profile" section header.
 * isExploreEnabled - Enables the third party SQL explore feature.
 * exploreUrlGenerator - Generates a URL to a third party SQL explorable website.
 */
interface TableProfileConfig {
  isBeta: boolean;
  isExploreEnabled: boolean;
  exploreUrlGenerator: (
    database: string,
    cluster: string,
    schema: string,
    table: string,
    partitionKey?: string,
    partitionValue?: string
  ) => string;
}

/**
 * FeatureLineageConfig - enable upstream lineage tab for features
 */
interface FeatureLineageConfig {
  inAppListEnabled: boolean;
}

/**
 * TableLineageDisableAppListLinksConfig - maps table fields to regular expressions or string lists
 * for matching and disabling list links if they don't match
 */
interface TableLineageDisableAppListLinksConfig {
  database?: RegExp;
  cluster?: RegExp;
  schema?: RegExp;
  table?: RegExp;
  badges?: string[];
}

/**
 * TableLineageConfig - Customize the "Table Lineage" links of the "Table Details" page.
 * This feature is intended to link to an external lineage provider.
 *
 * iconPath - Path to an icon image to display next to the lineage URL.
 * isBeta - Adds a "beta" tag to the section header.
 * isEnabled - Whether to show or hide this section
 * urlGenerator - Generate a URL to the third party lineage website
 * inAppListEnabled - Enable the in app Upstream/Downstream tabs for table lineage. Requires backend support.
 * inAppListMessages - when an in app list is enabled this will add a custom message at the end of the lineage tabs content.
 * disableAppListLinks - Set up table field based regular expression rules to disable lineage list view links.
 */
export interface TableLineageConfig {
  iconPath: string;
  isBeta: boolean;
  urlGenerator: (
    database: string,
    cluster: string,
    schema: string,
    table: string
  ) => string;
  externalEnabled: boolean;
  inAppListEnabled: boolean;
  inAppListMessageGenerator?: (
    direction: string,
    database: string,
    cluster: string,
    schema: string,
    table: string
  ) => string;
  inAppPageEnabled: boolean;
  disableAppListLinks?: TableLineageDisableAppListLinksConfig;
  defaultLineageDepth: number;
}

/**
 * ColumnLineageConfig - Configure column level lineage features in Amundsen.
 *
 * inAppListEnabled - whether the in-app column list lineage is enabled.
 * inAppPageEnabled - whether the in-app column lineage page is enabled.
 * urlGenerator - the lineage link for a given column
 */
interface ColumnLineageConfig {
  inAppListEnabled: boolean;
  inAppPageEnabled: boolean;
  urlGenerator: (
    database: string,
    cluster: string,
    schema: string,
    table: string,
    column: string
  ) => string;
}

interface Link {
  href: string;
  id: string;
  label: string;
  target?: string;
}

export interface LinkConfig extends Link {
  use_router: boolean;
}

export interface VisualLinkConfig extends Link {
  iconPath?: string;
}

/**
 * IndexDashboardsConfig - When enabled, dashboards will be avaialable as searchable resources. This requires
 * dashboards objects to be ingested via Databuilder and made available in the metadata and serch services.
 *
 * enabled - Enables/disables this feature in the frontend only
 */
interface IndexDashboardsConfig {
  enabled: boolean;
}

/**
 * IndexUsersConfig - When enabled, users will be avaialable as searchable resources. This requires
 * user objects to bed ingested via Databuilder and made available in the metadata and serch services.
 *
 * enabled - Enables/disables this feature in the frontend only
 */
interface IndexUsersConfig {
  enabled: boolean;
}

/**
 * IndexFeaturesConfig - When enabled, ML features will be avaialable as searchable resources. This requires
 * feature objects to be ingested via Databuilder and made available in the metadata and serch services.
 *
 * enabled - Enables/disables this feature in the frontend only
 */
interface IndexFeaturesConfig {
  enabled: boolean;
}

/**
 * EditableTextConfig - Configure max length limits for editable fields
 *
 * tableDescLength - maxlength for table descriptions
 * columnDescLength - maxlength for column descriptions
 */
interface EditableTextConfig {
  tableDescLength: number;
  columnDescLength: number;
}
/**
 * IssueTrackingConfig - configures whether to display the issue tracking feature
 * that allows users to display tickets associated with a table and create ones
 * linked to a table
 *
 * issueDescriptionTemplate - prepopulated in the description for reporting an issue
 *
 * NOTE: project selection is currently only implemented for Jira issue tracking
 * projectSelection.enabled - allows users to override the default project in which to create the issue
 * projectSelection.title - title for selection field that allows more specificity in what you ask the user to enter
 * projectSelection.inputHint - hint to show the user what type of value is expected, such as the name of the
 *                              default project
 */
interface IssueTrackingConfig {
  enabled: boolean;
  issueDescriptionTemplate?: string;
  projectSelection?: {
    enabled: boolean;
    title: string;
    inputHint?: string;
  };
}

// @deprecate - this is not being used at the moment
export enum NumberStyle {
  DECIMAL = 'decimal',
  CURRENCY = 'currency',
  PERCENT = 'percent',
  UNIT = 'unit',
}

// @deprecate - this is not being used at the moment
export interface NumberStyleConfig {
  style: NumberStyle;
  config: string;
}

/**
 * NumberFormatConfig - configurations for formatting different type of numbers like currency, and percentages in the desired format
 */
export interface NumberFormatConfig {
  numberSystem: string | null;
  // @deprecate - this is not being used at the moment
  [NumberStyle.DECIMAL]?: NumberStyleConfig;
}

/**
 * TableQualityChecksConfig - configuration to query and display data quality check status from
 * an external provider. API must be configured.
 */
export interface TableQualityChecksConfig {
  isEnabled: boolean;
}

export interface NestedColumnConfig {
  maxNestedColumns: number;
}

/**
 * Configuration for all tours for the application
 */
export interface ToursConfig {
  /**
   * Path on the application where the tours will apply
   */
  [path: string]: TourConfig[];
}

/**
 * Configuration for one instance of a Product tour
 */
export interface TourConfig {
  /**
   * Whether the tour is a tour of the page (false) or if it is a tour
   * for a single feature inside the page
   */
  isFeatureTour: boolean;
  /**
   * Whether the tour will automatically show up on the first time the user
   * visits the page.
   */
  isShownOnFirstVisit: boolean;
  /**
   * Whether there will be a button to start the tour at any time the user
   * wants to see it again.
   */
  isShownProgrammatically: boolean;
  /**
   * The list of steps that the tour will show.
   */
  steps: TourStep[];
}

/**
 * Describes a single step of the product tour
 */
export interface TourStep {
  /**
   * CSS selector for the element to highlight
   */
  target: string;
  /**
   * Title of the tour step (if any)
   */
  title?: string;
  /**
   * Content for the tour step
   */
  content: string;
  /**
   * Whether the step will show a beacon
   */
  disableBeacon?: boolean;
}

/**
 * Configuration for search results pagination
 */
export interface SearchPagination {
  /**
   * Number of results per page
   */
  resultsPerPage: number;
}

export interface HomePageWidgetsConfig {
  /**
   * Configuration for homepage widgets
   */
  widgets: Widget[];
}
