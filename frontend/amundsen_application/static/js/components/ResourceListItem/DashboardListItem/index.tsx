// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import { logClick } from 'utils/analytics';
import { buildDashboardURL } from 'utils/navigationUtils';
import { formatDate } from 'utils/dateUtils';

import { ResourceType, DashboardResource } from 'interfaces';

import { NO_TIMESTAMP_TEXT } from '../../../constants';
import { LoggingParams } from '../types';
import { HighlightedDashboard } from '../MetadataHighlightList/utils';
import MetadataHighlightList from '../MetadataHighlightList';
import * as Constants from './constants';

export interface DashboardListItemProps {
  dashboard: DashboardResource;
  logging: LoggingParams;
  dashboardHighlights: HighlightedDashboard;
}

class DashboardListItem extends React.Component<DashboardListItemProps, {}> {
  getLink = () => {
    const { dashboard, logging } = this.props;

    return `${buildDashboardURL(dashboard.uri)}?index=${logging.index}&source=${
      logging.source
    }`;
  };

  generateResourceIconClass = (
    dashboardId: string,
    dashboardType: ResourceType
  ): string =>
    `icon resource-icon ${getSourceIconClass(dashboardId, dashboardType)}`;

  render() {
    const { dashboard, logging, dashboardHighlights } = this.props;
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
                dashboard.product,
                dashboard.type
              )}
            />
            <div className="resource-info-text my-auto">
              <div className="resource-name">
                <div className="dashboard-name">{dashboard.name}</div>
                <div className="dashboard-group truncated">
                  {dashboard.group_name}
                </div>
                <BookmarkIcon
                  bookmarkKey={dashboard.uri}
                  resourceType={dashboard.type}
                />
              </div>
              <span className="description-section">
                {dashboard.description && (
                  <div
                    className="description text-body-w3 truncated"
                    dangerouslySetInnerHTML={{
                      __html: dashboardHighlights.description,
                    }}
                  />
                )}
              </span>
              {dashboardHighlights.chartNames && (
                <MetadataHighlightList
                  fieldName="chart names"
                  highlightedMetadataList={dashboardHighlights.chartNames}
                />
              )}
              {dashboardHighlights.queryNames && (
                <MetadataHighlightList
                  fieldName="query names"
                  highlightedMetadataList={dashboardHighlights.queryNames}
                />
              )}
            </div>
          </div>
          <div className="resource-type resource-source">
            {getSourceDisplayName(dashboard.product, dashboard.type)}
          </div>
          <div className="resource-badges">
            <div>
              <div className="title-3">{Constants.LAST_RUN_TITLE}</div>
              <time className="body-secondary-3">
                {dashboard.last_successful_run_timestamp
                  ? formatDate({
                      epochTimestamp: dashboard.last_successful_run_timestamp,
                    })
                  : NO_TIMESTAMP_TEXT}
              </time>
            </div>
            <img className="icon icon-right" alt="" />
          </div>
        </Link>
      </li>
    );
  }
}

export default DashboardListItem;
