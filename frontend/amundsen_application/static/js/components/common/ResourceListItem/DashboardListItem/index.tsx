import * as React from 'react';
import * as Avatar from 'react-avatar';
import { Link } from 'react-router-dom';

import { LoggingParams } from '../types';

import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import { ResourceType, DashboardResource } from 'interfaces';

import { formatDate } from 'utils/dateUtils';

import * as Constants from './constants';

export interface DashboardListItemProps {
  dashboard: DashboardResource;
  logging: LoggingParams;
}

class DashboardListItem extends React.Component<DashboardListItemProps, {}> {
  getLink = () => {
    const { dashboard, logging } = this.props;
    return `/dashboard?uri=${dashboard.uri}&index=${logging.index}&source=${logging.source}`;
  };

  generateResourceIconClass = (dashboardId: string, dashboardType: ResourceType): string => {
    return `icon resource-icon ${getSourceIconClass(dashboardId, dashboardType)}`;
  };

  render() {
    const { dashboard } = this.props;
    return (
      <li className="list-group-item clickable">
        <Link className="resource-list-item table-list-item" to={ this.getLink() }>
          <div className="resource-info">
            <span className={this.generateResourceIconClass(dashboard.product, dashboard.type)} />
            <div className="resource-info-text my-auto">
              <div className="resource-name title-2">
                <div className="dashboard-group">
                  { dashboard.group_name }
                </div>
                <div className="dashboard-name truncated">
                  { dashboard.name }
                </div>
                <BookmarkIcon bookmarkKey={ dashboard.uri } resourceType={ dashboard.type } />
              </div>
              <div className="body-secondary-3 truncated">{ dashboard.description }</div>
            </div>
          </div>
          <div className="resource-type">
            { getSourceDisplayName(dashboard.product, dashboard.type) }
          </div>
          <div className="resource-badges">
            {
               dashboard.last_successful_run_timestamp &&
               <div>
                 <div className="title-3">{ Constants.LAST_RUN_TITLE }</div>
                 <div className="body-secondary-3">
                   { formatDate({ epochTimestamp: dashboard.last_successful_run_timestamp }) }
                 </div>
               </div>
             }
            <img className="icon icon-right" />
          </div>
        </Link>
      </li>
    );
  }
}

export default DashboardListItem;
