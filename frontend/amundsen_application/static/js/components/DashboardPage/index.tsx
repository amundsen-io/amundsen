import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { RouteComponentProps } from 'react-router';
import * as qs from 'simple-query-string';

import AvatarLabel from 'components/common/AvatarLabel';
import Breadcrumb from 'components/common/Breadcrumb';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import Flag from 'components/common/Flag';
import EditableSection from 'components/common/EditableSection';
import LoadingSpinner from 'components/common/LoadingSpinner';
import TabsComponent from 'components/common/TabsComponent';
import { getDashboard } from 'ducks/dashboard/reducer';
import { GetDashboardRequest } from 'ducks/dashboard/types';
import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'ducks/utilMethods';
import { DashboardMetadata } from 'interfaces/Dashboard';
import ImagePreview from './ImagePreview';
import QueryList from 'components/DashboardPage/QueryList';
import ChartList from 'components/DashboardPage/ChartList';
import { formatDateTimeShort } from '../../utils/dateUtils';
import ResourceList from 'components/common/ResourceList';
import {
  ADD_DESC_TEXT,
  EDIT_DESC_TEXT,
  DASHBOARD_OWNER_SOURCE,
  DASHBOARD_SOURCE,
  LAST_RUN_SUCCEEDED,
  NO_OWNER_TEXT,
  TABLES_PER_PAGE
} from 'components/DashboardPage/constants';
import TagInput from 'components/Tags/TagInput';
import { ResourceType } from 'interfaces';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import { getLoggingParams } from 'utils/logUtils';

import './styles.scss';

export interface RouteProps {
  uri: string;
}

interface DashboardPageState {
  uri: string;
}

export interface StateFromProps {
  isLoading: boolean;
  statusCode: number;
  dashboard: DashboardMetadata;
}

export interface DispatchFromProps {
  getDashboard: (payload: { uri: string, searchIndex?: string, source?: string }) => GetDashboardRequest;
}

export type DashboardPageProps = RouteComponentProps<RouteProps> & StateFromProps & DispatchFromProps;

export class DashboardPage extends React.Component<DashboardPageProps, DashboardPageState> {
  constructor(props) {
    super(props);

    const { uri } = qs.parse(this.props.location.search);
    this.state = { uri };
  }

  componentDidMount() {
    this.loadDashboard(this.state.uri);
  }

  loadDashboard(uri: string) {
    const { index, source } = getLoggingParams(this.props.location.search);
    this.props.getDashboard({ source, uri, searchIndex: index });
  }

  componentDidUpdate() {
    const { uri } = qs.parse(this.props.location.search);
    if (this.state.uri !== uri) {
      this.setState({ uri });
      this.loadDashboard(uri);
    }
  };

  mapStatusToStyle = (status: string): string => {
    if (status === LAST_RUN_SUCCEEDED) {
      return 'success';
    }
    return 'danger';
  };

  renderTabs() {
    const tabInfo = [];
    tabInfo.push({
      content:
        (
          <ResourceList
            allItems={ this.props.dashboard.tables }
            itemsPerPage={ TABLES_PER_PAGE }
            source={ DASHBOARD_SOURCE }
          />
        ),
      key: 'tables',
      title: `Tables (${this.props.dashboard.tables.length})`,
    });

    if (this.props.dashboard.chart_names.length > 0 ) {
      tabInfo.push({
        content: <ChartList charts={ this.props.dashboard.chart_names }/>,
        key: 'charts',
        title: `Charts (${this.props.dashboard.chart_names.length})`,
      });
    };

    tabInfo.push({
      content: <QueryList queries={ this.props.dashboard.query_names }/>,
      key: 'queries',
      title: `Queries (${this.props.dashboard.query_names.length})`,
    });

    return <TabsComponent tabs={ tabInfo } defaultTab={ "tables" } />;
  }

  render() {
    const { dashboard, isLoading } = this.props;
    const hasDescription = dashboard.description && dashboard.description.length > 0;

    if (isLoading) {
      return <LoadingSpinner/>;
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
            <span className={`icon icon-header ${getSourceIconClass(dashboard.product, ResourceType.dashboard)}`}/>
          </div>
          <div className="header-section header-title">
            <h3 className="header-title-text truncated">
              { dashboard.name }
            </h3>
            <BookmarkIcon bookmarkKey={ dashboard.uri } resourceType={ ResourceType.dashboard } />
            <div className="body-2">
              Dashboard
              <Flag text="beta" labelStyle="default"/>
              in&nbsp;
              <a id="dashboard-group-link"
                 onClick={ logClick }
                 href={ dashboard.group_url }
                 target="_blank"
                 rel="noopener noreferrer"
              >
                 { dashboard.group_name }
              </a>
            </div>
          </div>
          {/* <div className="header-section header-links">links here</div> */}
          <div className="header-section header-buttons">
            <a id="dashboard-link"
               target="_blank"
               href={ dashboard.url }
               onClick={ logClick }
               className="btn btn-default btn-lg"
               rel="noopener noreferrer"
            >
              Open Dashboard
            </a>
          </div>
        </header>
        <article className="column-layout-1">
          <section className="left-panel">
            <EditableSection
              title="Description"
              readOnly={ true }
              editUrl={ dashboard.url }
              editText={`${EDIT_DESC_TEXT} ${getSourceDisplayName(dashboard.product, ResourceType.dashboard)}`}
            >
              {
                hasDescription &&
                <div className="body-2 and text-primary">
                  { dashboard.description }
                </div>
              }
              {
                !hasDescription &&
                <a
                 className="edit-link body-2"
                 target="_blank"
                 href={ dashboard.url }
                 rel="noopener noreferrer"
                >
                 {`${ADD_DESC_TEXT} ${getSourceDisplayName(dashboard.product, ResourceType.dashboard)}`}
                </a>
              }
            </EditableSection>
            <section className="column-layout-2">
              <section className="left-panel">
                <section className="metadata-section">
                  <div className="section-title title-3">Owners</div>
                  <div>
                    {
                      dashboard.owners.length > 0 &&
                      dashboard.owners.map(owner =>
                        <Link
                          key={owner.user_id}
                          to={`/user/${owner.user_id}?source=${DASHBOARD_OWNER_SOURCE}`}>
                          <AvatarLabel
                            label={owner.display_name}/>
                        </Link>
                      )
                    }
                    {
                      dashboard.owners.length === 0 &&
                      <AvatarLabel
                        avatarClass='gray-avatar'
                        labelClass='text-placeholder'
                        label={NO_OWNER_TEXT}
                      />
                    }
                  </div>
                </section>
                <section className="metadata-section">
                  <div className="section-title title-3">Created</div>
                  <div className="body-2 text-primary">
                    { formatDateTimeShort({ epochTimestamp: dashboard.created_timestamp}) }
                  </div>
                </section>
                <section className="metadata-section">
                  <div className="section-title title-3">Last Updated</div>
                  <div className="body-2 text-primary">
                    { formatDateTimeShort({ epochTimestamp: dashboard.updated_timestamp }) }
                  </div>
                </section>
                <section className="metadata-section">
                  <div className="section-title title-3">Recent View Count</div>
                  <div className="body-2 text-primary">
                    { dashboard.recent_view_count }
                  </div>
                </section>
              </section>
              <section className="right-panel">
                <EditableSection title="Tags">
                  <TagInput
                    resourceType={ ResourceType.dashboard }
                    uriKey={ this.props.dashboard.uri }
                  />
                </EditableSection>
                <section className="metadata-section">
                  <div className="section-title title-3">Last Successful Run</div>
                  <div className="body-2 text-primary">
                    { formatDateTimeShort({ epochTimestamp: dashboard.last_successful_run_timestamp }) }
                  </div>
                </section>
                <section className="metadata-section">
                  <div className="section-title title-3">Last Run</div>
                  <div>
                    <div className="body-2 text-primary">
                      { formatDateTimeShort({ epochTimestamp: dashboard.last_run_timestamp }) }
                    </div>
                    <div className="last-run-state">
                      <Flag
                        caseType='sentenceCase'
                        text={ dashboard.last_run_state }
                        labelStyle={this.mapStatusToStyle(dashboard.last_run_state)}
                      />
                    </div>
                  </div>
                </section>
              </section>
            </section>
            <ImagePreview uri={this.state.uri} redirectUrl={dashboard.url} />
          </section>
          <section className="right-panel">
            { this.renderTabs() }
          </section>
        </article>
      </div>
   );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    isLoading: state.dashboard.isLoading,
    statusCode: state.dashboard.statusCode,
    dashboard: state.dashboard.dashboard,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getDashboard } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(DashboardPage);
