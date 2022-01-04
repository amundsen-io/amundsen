// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import { logClick } from 'utils/analytics';
import { buildReportURL } from 'utils/navigationUtils';
import { formatDate } from 'utils/dateUtils';

import { ResourceType, ReportResource } from 'interfaces';

import { NO_TIMESTAMP_TEXT } from '../../../constants';
import * as Constants from './constants';
import { LoggingParams } from '../types';

export interface ReportListItemProps {
  report: ReportResource;
  logging: LoggingParams;
}

class ReportListItem extends React.Component<ReportListItemProps, {}> {
  getLink = () => {
    const { report, logging } = this.props;

    return `${buildReportURL(report.key)}?index=${logging.index}&source=${
      logging.source
    }`;
  };

  generateResourceIconClass = (
    dashboardId: string,
    dashboardType: ResourceType
  ): string =>
    `icon resource-icon ${getSourceIconClass(dashboardId, dashboardType)}`;

  render() {
    const { report, logging } = this.props;
    return (
      <li className="list-group-item clickable">
        <Link
          className="resource-list-item table-list-item"
          to={this.getLink()}
          onClick={(e) =>
            logClick(e, {
              target_id: 'dashboard_list_item',
              value: logging.source,
              position: logging.index.toString(),
            })
          }
        >
          <div className="resource-info">
            <span
              className={this.generateResourceIconClass(
                report.source,
                report.type
              )}
            />
            <div className="resource-info-text my-auto">
              <div className="resource-name">
                <div className="dashboard-name">{report.name}</div>
                <div className="dashboard-group truncated">
                  {report.workspace}
                </div>
              </div>
              <div className="body-secondary-3 truncated">
                {report.description}
              </div>
            </div>
          </div>
          <div className="resource-type">
            {getSourceDisplayName(report.source, report.type)}
          </div>
        </Link>
      </li>
    );
  }
}

export default ReportListItem;