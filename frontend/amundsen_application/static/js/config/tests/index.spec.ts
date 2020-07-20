import AppConfig from 'config/config';
import * as ConfigUtils from 'config/config-utils';
import { BadgeStyle } from 'config/config-types';

import { ResourceType } from 'interfaces';

describe('getSourceDisplayName', () => {
  it('returns given id if no config for that id exists', () => {
    const testId = 'fakeName';
    expect(ConfigUtils.getSourceDisplayName(testId, ResourceType.table)).toBe(
      testId
    );
  });

  it('returns given id for a configured source id', () => {
    const testId = 'hive';
    const expectedName =
      AppConfig.resourceConfig[ResourceType.table].supportedSources[testId]
        .displayName;
    expect(ConfigUtils.getSourceDisplayName(testId, ResourceType.table)).toBe(
      expectedName
    );
  });
});

describe('getSourceIconClass', () => {
  describe('if not config for the given id exists', () => {
    it('returns default class for dashboard', () => {
      const testId = 'fakeName';
      expect(
        ConfigUtils.getSourceIconClass(testId, ResourceType.dashboard)
      ).toBe(ConfigUtils.DEFAULT_DASHBOARD_ICON_CLASS);
    });

    it('returns default class for tables', () => {
      const testId = 'fakeName';
      expect(ConfigUtils.getSourceIconClass(testId, ResourceType.table)).toBe(
        ConfigUtils.DEFAULT_DATABASE_ICON_CLASS
      );
    });
  });

  it('returns empty string for unconfigured resource', () => {
    expect(ConfigUtils.getSourceIconClass('fakeName', ResourceType.user)).toBe(
      ''
    );
  });

  it('returns given icon class for a configured database id', () => {
    const testId = 'hive';
    const expectedClass =
      AppConfig.resourceConfig[ResourceType.table].supportedSources[testId]
        .iconClass;
    expect(ConfigUtils.getSourceIconClass(testId, ResourceType.table)).toBe(
      expectedClass
    );
  });
});

describe('getDisplayNameByResource', () => {
  it('returns the displayName for a given resource', () => {
    const testResource = ResourceType.table;
    const expectedValue = AppConfig.resourceConfig[testResource].displayName;
    expect(ConfigUtils.getDisplayNameByResource(testResource)).toBe(
      expectedValue
    );
  });
});

describe('getFilterConfigByResource', () => {
  it('returns the filter categories for a given resource', () => {
    const testResource = ResourceType.table;
    const expectedValue =
      AppConfig.resourceConfig[testResource].filterCategories;
    expect(ConfigUtils.getFilterConfigByResource(testResource)).toBe(
      expectedValue
    );
  });
});

describe('getBadgeConfig', () => {
  AppConfig.badges = {
    test_1: {
      style: BadgeStyle.DANGER,
      displayName: 'badge display value 1',
    },
    test_2: {
      style: BadgeStyle.DANGER,
      displayName: 'badge display value 2',
    },
  };

  it('Returns the badge config for a given badge', () => {
    const config = ConfigUtils.getBadgeConfig('test_1');
    const expectedConfig = AppConfig.badges.test_1;
    expect(config.style).toEqual(expectedConfig.style);
    expect(config.displayName).toEqual(expectedConfig.displayName);
  });

  it('Returns default badge config for unspecified badges', () => {
    const badgeName = 'not_configured_badge';
    const badgeConfig = ConfigUtils.getBadgeConfig(badgeName);
    expect(badgeConfig.style).toEqual(BadgeStyle.DEFAULT);
    expect(badgeConfig.displayName).toEqual('not configured badge');
  });
});

describe('feedbackEnabled', () => {
  it('returns whether or not the feaadback feature is enabled', () => {
    expect(ConfigUtils.feedbackEnabled()).toBe(
      AppConfig.mailClientFeatures.feedbackEnabled
    );
  });
});

describe('issueTrackingEnabled', () => {
  it('returns whether or not the issueTracking feature is enabled', () => {
    expect(ConfigUtils.issueTrackingEnabled()).toBe(
      AppConfig.issueTracking.enabled
    );
  });
});

describe('indexDashboardsEnabled', () => {
  it('returns whether or not the indexDashboards feature is enabled', () => {
    expect(ConfigUtils.indexDashboardsEnabled()).toBe(
      AppConfig.indexDashboards.enabled
    );
  });
});

describe('indexUsersEnabled', () => {
  it('returns whether or not the indexUsers feature is enabled', () => {
    expect(ConfigUtils.indexUsersEnabled()).toBe(AppConfig.indexUsers.enabled);
  });
});

describe('notificationsEnabled', () => {
  it('returns whether or not the notifications feature is enabled', () => {
    expect(ConfigUtils.notificationsEnabled()).toBe(
      AppConfig.mailClientFeatures.notificationsEnabled
    );
  });
});

describe('showAllTags', () => {
  it('returns whether or not to show all tags', () => {
    AppConfig.browse.showAllTags = true;
    expect(ConfigUtils.showAllTags()).toBe(AppConfig.browse.showAllTags);
    AppConfig.browse.showAllTags = false;
    expect(ConfigUtils.showAllTags()).toBe(AppConfig.browse.showAllTags);
  });
});

describe('getCuratedTags', () => {
  it('returns a list of curated tags', () => {
    AppConfig.browse.curatedTags = ['one', 'two', 'three'];
    expect(ConfigUtils.getCuratedTags()).toBe(AppConfig.browse.curatedTags);
  });
});

describe('exploreEnabled', () => {
  it('returns whether the explore function is enabled', () => {
    AppConfig.tableProfile.isExploreEnabled = true;
    expect(ConfigUtils.exploreEnabled()).toBe(
      AppConfig.tableProfile.isExploreEnabled
    );
    AppConfig.tableProfile.isExploreEnabled = false;
    expect(ConfigUtils.exploreEnabled()).toBe(
      AppConfig.tableProfile.isExploreEnabled
    );
  });
});

describe('generateExploreUrl', () => {
  const tableData = {
    badges: [],
    cluster: 'cluster',
    columns: [],
    dashboards: [],
    database: 'database',
    is_editable: false,
    is_view: false,
    key: '',
    schema: 'schema',
    name: 'table_name',
    last_updated_timestamp: 12321312312,
    description: '',
    table_writer: { application_url: '', description: '', id: '', name: '' },
    partition: {
      is_partitioned: true,
      key: 'partition_key',
      value: 'partition_value',
    },
    table_readers: [],
    source: { source: '', source_type: '' },
    resource_reports: [],
    watermarks: [],
    programmatic_descriptions: [],
  };

  it('calls `exploreUrlGenerator` with table metadata', () => {
    const exploreUrlGeneratorSpy = jest.spyOn(
      AppConfig.tableProfile,
      'exploreUrlGenerator'
    );
    ConfigUtils.generateExploreUrl(tableData);
    expect(exploreUrlGeneratorSpy).toBeCalledWith(
      tableData.database,
      tableData.cluster,
      tableData.schema,
      tableData.name,
      tableData.partition.key,
      tableData.partition.value
    );
  });

  it('excludes partition data if it does not exist', () => {
    const mockTableData = {
      ...tableData,
      partition: {
        is_partitioned: false,
      },
    };

    const exploreUrlGeneratorSpy = jest.spyOn(
      AppConfig.tableProfile,
      'exploreUrlGenerator'
    );
    ConfigUtils.generateExploreUrl(mockTableData);
    expect(exploreUrlGeneratorSpy).toBeCalledWith(
      mockTableData.database,
      mockTableData.cluster,
      mockTableData.schema,
      mockTableData.name
    );
  });
});
