// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';
import * as ReactMarkdown from 'react-markdown';

import { getDashboard } from 'ducks/dashboard/reducer';
import { GetDashboardRequest } from 'ducks/dashboard/types';
import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'ducks/utilMethods';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { updateSearchState } from 'ducks/search/reducer';

import Breadcrumb from 'components/Breadcrumb';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import EditableSection from 'components/EditableSection';
import LoadingSpinner from 'components/LoadingSpinner';
import TabsComponent, { TabInfo } from 'components/TabsComponent';
import ResourceStatusMarker from 'components/ResourceStatusMarker';
import ResourceList from 'components/ResourceList';
import TagInput from 'components/Tags/TagInput';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import { formatDateTimeShort } from 'utils/dateUtils';
import { getLoggingParams } from 'utils/logUtils';

import { ResourceType } from 'interfaces';
import { DashboardMetadata } from 'interfaces/Dashboard';
import { NO_TIMESTAMP_TEXT } from '../../constants';
import {
  ADD_DESC_TEXT,
  EDIT_DESC_TEXT,
  OWNER_HEADER_TEXT,
  DASHBOARD_SOURCE,
  TABLES_PER_PAGE,
  LAST_RUN_SUCCEEDED,
  STATUS_TEXT,
} from './constants';
import ChartList from './ChartList';
import QueryList from './QueryList';
import DashboardOwnerEditor from './DashboardOwnerEditor';

import ImagePreview from './ImagePreview';

import './styles.scss';

interface DashboardPageState {
  uri: string;
}

export interface StateFromProps {
  isLoading: boolean;
  statusCode: number | null;
  dashboard: DashboardMetadata;
}

export interface MatchProps {
  uri: string;
}

export interface DispatchFromProps {
  getDashboard: (payload: {
    uri: string;
    searchIndex?: string;
    source?: string;
  }) => GetDashboardRequest;
  searchDashboardGroup: (dashboardGroup: string) => UpdateSearchStateRequest;
}

export type DashboardPageProps = RouteComponentProps<MatchProps> &
  StateFromProps &
  DispatchFromProps;

export class DashboardPage extends React.Component<
  DashboardPageProps,
  DashboardPageState
> {
  constructor(props) {
    super(props);
    const { uri } = this.props.match.params;

    this.state = { uri };
  }

  componentDidMount() {
    const { index, source } = getLoggingParams(this.props.location.search);
    const { uri } = this.props.match.params;

    this.props.getDashboard({ source, uri, searchIndex: index });
    this.setState({ uri });
  }

  componentDidUpdate() {
    const { uri } = this.props.match.params;

    if (this.state.uri !== uri) {
      const { index, source } = getLoggingParams(this.props.location.search);
      this.setState({ uri });
      this.props.getDashboard({ source, uri, searchIndex: index });
    }
  }

  searchGroup = (e) => {
    const { dashboard, searchDashboardGroup } = this.props;
    logClick(e, {
      target_type: 'dashboard_group',
      label: dashboard.group_name,
    });
    searchDashboardGroup(dashboard.group_name);
  };

  mapStatusToBoolean = (status: string): boolean => {
    if (status === LAST_RUN_SUCCEEDED) {
      return true;
    }
    return false;
  };

  renderTabs() {
    const tabInfo: TabInfo[] = [];

    tabInfo.push({
      content: (
        <ResourceList
          allItems={this.props.dashboard.tables}
          itemsPerPage={TABLES_PER_PAGE}
          source={DASHBOARD_SOURCE}
        />
      ),
      key: 'tables',
      title: `Tables (${this.props.dashboard.tables.length})`,
    });

    if (this.props.dashboard.chart_names.length > 0) {
      tabInfo.push({
        content: <ChartList charts={this.props.dashboard.chart_names} />,
        key: 'charts',
        title: `Charts (${this.props.dashboard.chart_names.length})`,
      });
    }

    tabInfo.push({
      content: (
        <QueryList
          product={this.props.dashboard.product}
          queries={this.props.dashboard.queries}
        />
      ),
      key: 'queries',
      title: `Queries (${this.props.dashboard.queries.length})`,
    });

    return <TabsComponent tabs={tabInfo} defaultTab="tables" />;
  }

  render() {
    const { dashboard, isLoading } = this.props;
    const hasDescription =
      dashboard.description && dashboard.description.length > 0;
    const hasLastRunState =
      dashboard.last_run_state && dashboard.last_run_state.length > 0;

    if (isLoading) {
      return <LoadingSpinner />;
    }
    if (this.props.statusCode === 500) {
      return (
        <div className="container error-label">
          <Breadcrumb />
          <label>Something went wrong...</label>
        </div>
      );
    }

    return (
      <div className="resource-detail-layout dashboard-page">
        <header className="resource-header">
          <div className="header-section">
            <Breadcrumb />
            <span
              className={`icon icon-header ${getSourceIconClass(
                dashboard.product,
                ResourceType.dashboard
              )}`}
            />
          </div>
          <div className="header-section header-title">
            <h1 className="header-title-text truncated" title={dashboard.name}>
              {dashboard.name}
            </h1>
            <BookmarkIcon
              bookmarkKey={dashboard.uri}
              resourceType={ResourceType.dashboard}
            />
            <div className="body-2">
              Dashboard in&nbsp;
              <button
                type="button"
                className="btn btn-link body-2"
                data-type="dashboard-group-link"
                onClick={this.searchGroup}
              >
                {dashboard.group_name}
              </button>
            </div>
          </div>
          {/* <div className="header-section header-links">links here</div> */}
          <div className="header-section header-buttons">
            <a
              data-type="dashboard-group-link"
              target="_blank"
              href={dashboard.group_url}
              onClick={logClick}
              className="btn btn-default btn-lg dashboard-group"
              rel="noopener noreferrer"
            >
              Open Group
            </a>
            <a
              data-type="dashboard-link"
              target="_blank"
              href={dashboard.url}
              onClick={logClick}
              className="btn btn-default btn-lg"
              rel="noopener noreferrer"
            >
              Open Dashboard
            </a>
          </div>
        </header>
        <article className="column-layout-1">
          <aside className="left-panel">
            <EditableSection
              title="Description"
              readOnly
              editUrl={dashboard.url}
              editText={`${EDIT_DESC_TEXT} ${getSourceDisplayName(
                dashboard.product,
                ResourceType.dashboard
              )}`}
            >
              {hasDescription && (
                <div className="markdown-wrapper">
                  <ReactMarkdown>{dashboard.description}</ReactMarkdown>
                </div>
              )}
              {!hasDescription && (
                <a
                  className="edit-link body-2"
                  target="_blank"
                  href={dashboard.url}
                  rel="noopener noreferrer"
                >
                  {`${ADD_DESC_TEXT} ${getSourceDisplayName(
                    dashboard.product,
                    ResourceType.dashboard
                  )}`}
                </a>
              )}
            </EditableSection>
            <section className="column-layout-2">
              <section className="left-panel">
                <EditableSection title={OWNER_HEADER_TEXT} readOnly>
                  <DashboardOwnerEditor resourceType={ResourceType.dashboard} />
                </EditableSection>
                <section className="metadata-section">
                  <div className="section-title title-3">Created</div>
                  <time className="body-2 text-primary">
                    {formatDateTimeShort({
                      epochTimestamp: dashboard.created_timestamp,
                    })}
                  </time>
                </section>
                <section className="metadata-section">
                  <div className="section-title title-3">Last Updated</div>
                  <time className="body-2 text-primary">
                    {formatDateTimeShort({
                      epochTimestamp: dashboard.updated_timestamp,
                    })}
                  </time>
                </section>
                <section className="metadata-section">
                  <div className="section-title title-3">Recent View Count</div>
                  <div className="body-2 text-primary">
                    {dashboard.recent_view_count}
                  </div>
                </section>
              </section>
              <section className="right-panel">
                <EditableSection title="Tags">
                  <TagInput
                    resourceType={ResourceType.dashboard}
                    uriKey={this.props.dashboard.uri}
                  />
                </EditableSection>
                {hasLastRunState && [
                  <section className="metadata-section">
                    <div className="section-title title-3">
                      Last Successful Run
                    </div>
                    <time className="last-successful-run-timestamp body-2 text-primary">
                      {dashboard.last_successful_run_timestamp
                        ? formatDateTimeShort({
                            epochTimestamp:
                              dashboard.last_successful_run_timestamp,
                          })
                        : NO_TIMESTAMP_TEXT}
                    </time>
                  </section>,
                  <section className="metadata-section">
                    <div className="section-title title-3">Last Run</div>
                    <div>
                      <time className="last-run-timestamp body-2 text-primary">
                        {dashboard.last_run_timestamp
                          ? formatDateTimeShort({
                              epochTimestamp: dashboard.last_run_timestamp,
                            })
                          : NO_TIMESTAMP_TEXT}
                      </time>
                      <div className="last-run-state">
                        <span className="status">{STATUS_TEXT}</span>
                        <ResourceStatusMarker
                          stateText={dashboard.last_run_state}
                          succeeded={this.mapStatusToBoolean(
                            dashboard.last_run_state
                          )}
                        />
                      </div>
                    </div>
                  </section>,
                ]}
              </section>
            </section>
            <ImagePreview uri={this.state.uri} redirectUrl={dashboard.url} />
          </aside>
          <main className="right-panel">{this.renderTabs()}</main>
        </article>
      </div>
    );
  }
}

function searchDashboardGroup(
  dashboardGroup: string
): UpdateSearchStateRequest {
  return updateSearchState({
    filters: {
      [ResourceType.dashboard]: { group_name: dashboardGroup },
    },
    submitSearch: true,
  });
}

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.dashboard.isLoading,
  statusCode: state.dashboard.statusCode,
  dashboard: state.dashboard.dashboard,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getDashboard, searchDashboardGroup }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(DashboardPage);
