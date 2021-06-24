import AppConfig from 'config/config';
import * as ConfigUtils from 'config/config-utils';
import { BadgeStyle, NoticeSeverity } from 'config/config-types';

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
    const expectedName = (<any>AppConfig).resourceConfig[ResourceType.table]
      .supportedSources[testId].displayName;
    expect(expectedName).toBeDefined();
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
    const expectedClass = (<any>AppConfig).resourceConfig[ResourceType.table]
      .supportedSources[testId].iconClass;
    expect(expectedClass).toBeDefined();
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

describe('getResourceNotices', () => {
  describe('when resource is a table', () => {
    describe('when there is a notice', () => {
      it('returns the notice', () => {
        AppConfig.resourceConfig[ResourceType.table].notices = {
          testName: {
            severity: NoticeSeverity.WARNING,
            messageHtml: 'testMessage',
          },
        };
        const expected = 'testMessage';
        const notice = ConfigUtils.getResourceNotices(
          ResourceType.table,
          'testName'
        );
        const actual = notice && notice.messageHtml;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there are wildcards ', () => {
      describe('when there is a wildcard in cluster position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            '*.hive.core.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in cluster position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            '*.hive.coco.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there is a wildcard in datasource position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.*.core.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in datasource position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.*.coco.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there is a wildcard in schema position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.*.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in schema position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.*.dimension_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there is a wildcard in table position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.core.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in table position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.coco.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 2 wildcards in schema/table positions', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.*.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 2 notices that match', () => {
        it('returns the last matched notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.*.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
            'gold.hive.core.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage2',
            },
          };
          const expected = 'testMessage2';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 2 notices, but only one matches', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            'gold.hive.core.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage2',
            },
            'gold.hive.shadow.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage2';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 4 wildcards', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.table].notices = {
            '*.*.*.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.table,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });
    });

    describe('when there is a notice with a dynamic message', () => {
      it('returns notice with dynamic message', () => {
        AppConfig.resourceConfig[ResourceType.table].notices = {
          'gold.hive.core.fact_rides': {
            severity: NoticeSeverity.WARNING,
            messageHtml: (resourceName) => {
              const [cluster, datasource, schema, table] = resourceName.split(
                '.'
              );
              return `${cluster}, ${datasource}, ${schema}, ${table}`;
            },
          },
        };
        const expected = 'gold, hive, core, fact_rides';
        const notice = ConfigUtils.getResourceNotices(
          ResourceType.table,
          'gold.hive.core.fact_rides'
        );
        const actual = notice && notice.messageHtml;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there is a notice with a wildcard and dynamic message', () => {
      it('returns notice with dynamic message', () => {
        AppConfig.resourceConfig[ResourceType.table].notices = {
          'gold.hive.core.*': {
            severity: NoticeSeverity.WARNING,
            messageHtml: (resourceName) => {
              const [cluster, datasource, schema, table] = resourceName.split(
                '.'
              );
              return `${cluster}, ${datasource}, ${schema}, ${table}`;
            },
          },
        };
        const expected = 'gold, hive, core, fact_rides';
        const notice = ConfigUtils.getResourceNotices(
          ResourceType.table,
          'gold.hive.core.fact_rides'
        );
        const actual = notice && notice.messageHtml;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there is no notice', () => {
      it('returns false', () => {
        AppConfig.resourceConfig[ResourceType.table].notices = {
          testName: {
            severity: NoticeSeverity.WARNING,
            messageHtml: 'testMessage',
          },
        };
        const expected = false;
        const actual = ConfigUtils.getResourceNotices(
          ResourceType.table,
          'testNameNoThere'
        );
        expect(actual).toEqual(expected);
      });
    });
  });

  describe('when resource is a dashboard', () => {
    describe('when there is a notice', () => {
      it('returns the notice', () => {
        AppConfig.resourceConfig[ResourceType.dashboard].notices = {
          testName: {
            severity: NoticeSeverity.WARNING,
            messageHtml: 'testMessage',
          },
        };
        const expected = 'testMessage';
        const notice = ConfigUtils.getResourceNotices(
          ResourceType.dashboard,
          'testName'
        );
        const actual = notice && notice.messageHtml;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there are wildcards ', () => {
      describe('when there is a wildcard in cluster position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            '*.hive.core.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in cluster position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            '*.hive.coco.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there is a wildcard in datasource position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.*.core.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in datasource position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.*.coco.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there is a wildcard in schema position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.*.fact_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in schema position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.*.dimension_rides': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there is a wildcard in table position', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.core.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe("when there is a wildcard in table position that doesn't match", () => {
        it('returns false', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.coco.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = false;
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 2 wildcards in schema/table positions', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.*.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 2 notices that match', () => {
        it('returns the last matched notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.*.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
            'gold.hive.core.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage2',
            },
          };
          const expected = 'testMessage2';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 2 notices, but only one matches', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            'gold.hive.core.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage2',
            },
            'gold.hive.shadow.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage2';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });

      describe('when there are 4 wildcards', () => {
        it('returns notice', () => {
          AppConfig.resourceConfig[ResourceType.dashboard].notices = {
            '*.*.*.*': {
              severity: NoticeSeverity.WARNING,
              messageHtml: 'testMessage',
            },
          };
          const expected = 'testMessage';
          const notice = ConfigUtils.getResourceNotices(
            ResourceType.dashboard,
            'gold.hive.core.fact_rides'
          );
          const actual = notice && notice.messageHtml;

          expect(actual).toEqual(expected);
        });
      });
    });

    describe('when there is a notice with a dynamic message', () => {
      it('returns notice with dynamic message', () => {
        AppConfig.resourceConfig[ResourceType.dashboard].notices = {
          'gold.hive.core.fact_rides': {
            severity: NoticeSeverity.WARNING,
            messageHtml: (resourceName) => {
              const [cluster, datasource, schema, table] = resourceName.split(
                '.'
              );
              return `${cluster}, ${datasource}, ${schema}, ${table}`;
            },
          },
        };
        const expected = 'gold, hive, core, fact_rides';
        const notice = ConfigUtils.getResourceNotices(
          ResourceType.dashboard,
          'gold.hive.core.fact_rides'
        );
        const actual = notice && notice.messageHtml;

        expect(actual).toEqual(expected);
      });
    });

    describe('when there is a notice with a wildcard and dynamic message', () => {
      it('returns notice with dynamic message', () => {
        AppConfig.resourceConfig[ResourceType.dashboard].notices = {
          'gold.hive.core.*': {
            severity: NoticeSeverity.WARNING,
            messageHtml: (resourceName) => {
              const [cluster, datasource, schema, table] = resourceName.split(
                '.'
              );
              return `${cluster}, ${datasource}, ${schema}, ${table}`;
            },
          },
        };
        const expected = 'gold, hive, core, fact_rides';
        const notice = ConfigUtils.getResourceNotices(
          ResourceType.dashboard,
          'gold.hive.core.fact_rides'
        );
        const actual = notice && notice.messageHtml;

        expect(actual).toEqual(expected);
      });
    });
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

describe('getAnalyticsConfig', () => {
  it('returns the analytics configuration object', () => {
    const expectedValue = AppConfig.analytics;

    expect(ConfigUtils.getAnalyticsConfig()).toBe(expectedValue);
  });
});

describe('getUniqueValueStatTypeName', () => {
  it('returns the unique value stat type key name', () => {
    const expectedValue = 'test';

    AppConfig.resourceConfig[ResourceType.table].stats = {
      uniqueValueTypeName: expectedValue,
    };

    expect(ConfigUtils.getUniqueValueStatTypeName()).toBe(expectedValue);
  });
});

describe('getTableSortCriterias', () => {
  it('returns the sorting criterias for tables', () => {
    const expectedValue =
      AppConfig.resourceConfig[ResourceType.table].sortCriterias;

    expect(ConfigUtils.getTableSortCriterias()).toBe(expectedValue);
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
    const badgeName = 'Not_configured_badge';
    const badgeConfig = ConfigUtils.getBadgeConfig(badgeName);
    expect(badgeConfig.style).toEqual(BadgeStyle.DEFAULT);
    expect(badgeConfig.displayName).toEqual(badgeName);
  });
});

describe('getNavLinks', () => {
  const testNavLinks = [
    {
      label: 'TestLabel1',
      id: 'nav::testPage1',
      href: '/testPage1',
      use_router: true,
    },
    {
      label: 'TestLabel2',
      id: 'nav::testPage2',
      href: '/testPage2',
      use_router: true,
    },
  ];
  AppConfig.navLinks = [
    ...testNavLinks,
    {
      label: 'Announcements',
      id: 'nav::announcements',
      href: '/announcements',
      use_router: true,
    },
  ];

  describe('when announcements is active', () => {
    it('returns all the navLinks', () => {
      AppConfig.announcements.enabled = true;
      const actual = ConfigUtils.getNavLinks();
      const expected = AppConfig.navLinks;

      expect(actual).toEqual(expected);
    });
  });

  describe('when announcements is deactivated', () => {
    it('returns all the navLinks but the announcements', () => {
      AppConfig.announcements.enabled = false;
      const actual = ConfigUtils.getNavLinks();
      const expected = testNavLinks;

      expect(actual).toEqual(expected);
    });
  });
});

describe('feedbackEnabled', () => {
  it('returns whether or not the feaadback feature is enabled', () => {
    expect(ConfigUtils.feedbackEnabled()).toBe(
      AppConfig.mailClientFeatures.feedbackEnabled
    );
  });
});

describe('announcementsEnabled', () => {
  it('returns whether or not the announcements feature is enabled', () => {
    expect(ConfigUtils.announcementsEnabled()).toBe(
      AppConfig.announcements.enabled
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
    programmatic_descriptions: {},
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

describe('numberFormat', () => {
  it('returns number format defined in config', () => {
    const actual = ConfigUtils.getNumberFormat();
    const expected = AppConfig.numberFormat;
    expect(actual).toBe(expected);
  });
});

describe('getDocumentTitle', () => {
  it('returns documentTitle defined in config', () => {
    const actual = ConfigUtils.getDocumentTitle();
    const expected = AppConfig.documentTitle;
    expect(actual).toBe(expected);
  });
});

describe('getLogoTitle', () => {
  it('returns logoTitle defined in config', () => {
    const actual = ConfigUtils.getLogoTitle();
    const expected = AppConfig.logoTitle;
    expect(actual).toBe(expected);
  });
});

describe('isTableListLineageEnabled', () => {
  it('returns isTableListLineageEnabled defined in config', () => {
    const actual = ConfigUtils.isTableListLineageEnabled();
    const expected = AppConfig.tableLineage.inAppListEnabled;
    expect(actual).toBe(expected);
  });
});

describe('isColumnListLineageEnabled', () => {
  it('returns isColumnListLineageEnabled defined in config', () => {
    const actual = ConfigUtils.isColumnListLineageEnabled();
    const expected = AppConfig.columnLineage.inAppListEnabled;
    expect(actual).toBe(expected);
  });
});

describe('isTableLineagePageEnabled', () => {
  it('returns isTableLineagePageEnabled defined in config', () => {
    const actual = ConfigUtils.isTableLineagePageEnabled();
    const expected = AppConfig.tableLineage.inAppPageEnabled;
    expect(actual).toBe(expected);
  });
});

describe('isColumnLineagePageEnabled', () => {
  it('returns isColumnLineagePageEnabled defined in config', () => {
    const actual = ConfigUtils.isColumnLineagePageEnabled();
    const expected = AppConfig.columnLineage.inAppPageEnabled;
    expect(actual).toBe(expected);
  });
});

describe('getColumnLineageLink', () => {
  it('calls the column lineage link with the right params', () => {
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
      programmatic_descriptions: {},
    };
    const columnName = 'column_name';
    const actual = ConfigUtils.getColumnLineageLink(tableData, columnName);
    const expected = AppConfig.columnLineage.urlGenerator(
      tableData.database,
      tableData.cluster,
      tableData.schema,
      tableData.name,
      columnName
    );
    expect(actual).toBe(expected);
  });
});
