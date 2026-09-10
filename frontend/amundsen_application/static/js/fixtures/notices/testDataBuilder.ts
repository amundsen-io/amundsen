// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { NoticeSeverity } from 'config/config-types';
import { DynamicResourceNotice } from 'interfaces';

/**
 * Generates test data for the notices API
 * @example
 * const testData = new NoticesTestDataBuilder()
 *                         .withQualityIssue()
 *                         .build();
 */
export default class NoticesTestDataBuilder {
  private notices: DynamicResourceNotice[];

  constructor() {
    this.notices = [];
  }

  withQualityIssue(): NoticesTestDataBuilder {
    this.notices = [
      ...this.notices,
      {
        payload: {
          id: 'vcfe1',
          last_updated: 'Mon, 30 Jan 2023 18:10:09 GMT',
          link: 'link-to-vcfe/1',
          owner: 'fr_verity_check_owner_1@lyft.com',
        },
        message: 'There is a data quality issue on this table.',
        severity: NoticeSeverity.WARNING,
      },
    ];

    return this;
  }

  withTableLandingIssue(): NoticesTestDataBuilder {
    this.notices = [
      ...this.notices,
      {
        payload: {
          id: 'abc123',
          last_updated: 'Mon, 30 Jan 2023 18:10:09 GMT',
          link: 'url-path/for-table-landing-monitor-breach',
          owner: 'fr_landing_breach_owner@lyft.com',
        },
        message: 'There is a table landing issue on this table.',
        severity: NoticeSeverity.WARNING,
      },
    ];

    return this;
  }

  withSEVIssue(): NoticesTestDataBuilder {
    this.notices = [
      ...this.notices,
      {
        payload: {
          id: 'ase1',
          last_updated: 'Mon, 30 Jan 2023 18:10:09 GMT',
          link: 'link-to-sev/1',
          owner: 'fr_sev_owner1@lyft.com',
        },
        message: 'There is an active SEV against this table.',
        severity: NoticeSeverity.WARNING,
      },
    ];

    return this;
  }

  withDAGIssue(): NoticesTestDataBuilder {
    this.notices = [
      ...this.notices,
      {
        payload: {
          id: 'fde1',
          last_updated: 'Mon, 30 Jan 2023 18:10:09 GMT',
          link: 'airflow.lyft.net/graph?dag_id=some_broken_dag',
          owner: 'fr_dag_owner1@lyft.com',
        },
        message: 'There is a failed DAG affecting this table.',
        severity: NoticeSeverity.WARNING,
      },
    ];

    return this;
  }

  withIssueOfSeverity(severity: NoticeSeverity): NoticesTestDataBuilder {
    this.notices = [
      ...this.notices,
      {
        payload: {
          id: 'id',
          last_updated: 'Mon, 30 Jan 2023 18:10:09 GMT',
          link: 'URL',
          owner: 'issue_owner@lyft.com',
        },
        message: 'There is a failed DAG affecting this table.',
        severity,
      },
    ];

    return this;
  }

  build(): DynamicResourceNotice[] {
    return this.notices;
  }
}

export const aNoticeTestData = (): NoticesTestDataBuilder =>
  new NoticesTestDataBuilder();
