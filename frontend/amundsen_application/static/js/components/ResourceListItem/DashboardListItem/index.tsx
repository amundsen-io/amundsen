// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import { buildDashboardURL } from 'utils/navigation';
import { formatDate } from 'utils/date';

import { ResourceType, DashboardResource } from 'interfaces';

import { LogSearchEventRequest } from 'ducks/log/types';
import { connect } from 'react-redux';
import { logSearchEvent } from 'ducks/log/reducer';
import { bindActionCreators } from 'redux';
import { NO_TIMESTAMP_TEXT } from '../../../constants';
import { LoggingParams } from '../types';
import { HighlightedDashboard } from '../MetadataHighlightList/utils';
import MetadataHighlightList from '../MetadataHighlightList';
import * as Constants from './constants';

export interface OwnProps {
  dashboard: DashboardResource;
  logging: LoggingParams;
  dashboardHighlights: HighlightedDashboard;
}

export interface DispatchFromProps {
  logSearchEvent: (
    resourceLink: string,
    resourceType: ResourceType,
    source: string,
    index: number,
    event: any,
    inline: boolean,
    extra?: { [key: string]: any }
  ) => LogSearchEventRequest;
}

export type DashboardListItemProps = OwnProps & DispatchFromProps;

export class DashboardListItem extends React.Component<
  DashboardListItemProps,
  {}
> {
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
    const { dashboard, logging, dashboardHighlights, logSearchEvent } =
      this.props;

    return (
      <li className="list-group-item clickable">
        <Link
          className="resource-list-item table-list-item"
          to={this.getLink()}
          onClick={(e) =>
            logSearchEvent(
              this.getLink(),
              ResourceType.dashboard,
              logging.source,
              logging.index,
              e,
              false
            )
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

export const mapDispatchToProps = (dispatch: any): DispatchFromProps => {
  const dispatchableActions: DispatchFromProps = bindActionCreators(
    {
      logSearchEvent,
    },
    dispatch
  );

  return dispatchableActions;
};
export default connect<{}, DispatchFromProps, OwnProps>(
  null,
  mapDispatchToProps
)(DashboardListItem);
