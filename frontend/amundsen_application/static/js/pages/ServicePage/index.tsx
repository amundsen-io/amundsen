import * as React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { bindActionCreators } from 'redux';
import * as DocumentTitle from 'react-document-title';
import { RouteComponentProps } from 'react-router';

import { GlobalState } from 'ducks/rootReducer';
import { getService } from 'ducks/service/reducer';
import { GetServiceRequest } from 'ducks/service/types';

import Breadcrumb from 'components/Breadcrumb';
import LoadingSpinner from 'components/LoadingSpinner';

import * as Constants from './constants';
import { getLoggingParams } from 'utils/navigationUtils';
import { ResourceType, ServiceMetaData } from 'interfaces';

import { getSourceIconClass } from 'config/config-utils';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import TabsComponent, { TabInfo } from 'components/TabsComponent';

import './styles.scss';

import SourceLink from './SourceLink';
import AttributeList from 'features/AttributeList';
import { formatDateTimeShort } from 'utils/dateUtils';
import { updateSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateRequest } from 'ducks/search/types';

const SERVER_ERROR_CODE = 500;

export interface PropsFromState {
  isLoading: boolean;
  statusCode: number | null;
  serviceData: ServiceMetaData;
}
export interface DispatchFromProps {
  getService: (
    key: string,
    index?: string,
    source?: string
  ) => GetServiceRequest;
  searchSchema: (schemaText: string) => UpdateSearchStateRequest;
}

export interface MatchProps {
  key: string;
}

export type ServiceDetailProps = PropsFromState &
  DispatchFromProps &
  RouteComponentProps<MatchProps>;

const ErrorMessage = () => (
  <div className="container error-label">
    <Breadcrumb />
    <label>{Constants.ERROR_MESSAGE}</label>
  </div>
);

export interface StateProps {}

export class ServiceDetail extends React.Component<
  ServiceDetailProps & RouteComponentProps<any>,
  StateProps
> {
  private key: string;
  private didComponentMount: boolean = false;

  state = {
    currentTab: this.getDefaultTab(),
  };

  componentDidMount() {
    const { location, getService } = this.props;
    const { index, source } = getLoggingParams(location.search);
    const {
      match: { params },
    } = this.props;
    this.key = params.key;
    getService(this.key, index, source);
    this.didComponentMount = true;
  }

  componentDidUpdate() {
    const {
      location,
      getService,
      match: { params },
    } = this.props;
    const newKey = params.key;
    if (this.key !== newKey) {
      const { index, source } = getLoggingParams(location.search);
      this.key = newKey;
      getService(this.key, index, source);
    }
  }

  handleClick = (e) => {
    const { match, searchSchema } = this.props;
    const { params } = match;
    const schemaText = params.schema;
    searchSchema(schemaText);
  };

  getDefaultTab() {
    return Constants.SERVICE_TAB.ATTRIBUTE;
  }

  getDisplayName() {
    const { match } = this.props;
    const { params } = match;
    return params.key;
  }

  renderTabs() {

    const { serviceData } = this.props;
    const tabInfo: TabInfo[] = [
      {
        content: <AttributeList attributes={serviceData?.attributes} />,
        key: Constants.SERVICE_TAB.ATTRIBUTE,
        title: `Attributes (${serviceData?.attributes?.length})`,
      },
    ];

    return (
      <TabsComponent
        tabs={tabInfo}
        defaultTab={Constants.SERVICE_TAB.ATTRIBUTE}
        onSelect={(key) => {
          this.setState({ currentTab: key });
        }}
      />
    );
  }

  render() {
    let innerContent;
    const { isLoading, statusCode, serviceData } = this.props;

    if (isLoading || !this.didComponentMount) innerContent = <LoadingSpinner />;
    else if (statusCode === SERVER_ERROR_CODE) innerContent = <ErrorMessage />;
    else {
      const data = serviceData;
      innerContent = (
        <div className="resource-detail-layout service-detail">
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <span
                className={
                  'icon icon-header ' +
                  getSourceIconClass(data.key, ResourceType.service)
                }
              />
            </div>
            <div className="header-section header-title">
              <h1 className="header-title-text truncated" title={data.name}>
                {data.name}
              </h1>
              <BookmarkIcon
                bookmarkKey={data.key}
                resourceType={ResourceType.service}
              />
              <div className="body-2">
                <ul className="header-bullets">
                  <li>
                    <Link to="/search" onClick={this.handleClick}>
                      Services
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
            <div className="header-section header-links">
              <SourceLink
                serviceSource={{
                  source:
                    data?.git_repo && data?.git_repo !== 'N/A'
                      ? data?.git_repo
                      : null,
                  source_type: 'github',
                }}
              />
              <SourceLink
                serviceSource={{
                  source:
                    data?.victor_ops && data?.victor_ops !== 'N/A'
                      ? data?.victor_ops
                      : null,
                  source_type: 'victorOps',
                }}
              />
            </div>
          </header>
          <div className="column-layout-1">
            <aside className="left-panel">
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">
                  {Constants.DESCRIPTION_TITLE}
                </h3>
                {data.description}
              </section>
              <section className="column-layout-2">
                <section className="left-panel">
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.OWNERS_TITLE}
                    </h3>
                    {data?.owned_by || 'N/A'}
                  </section>
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.CREATED_TITLE}
                    </h3>
                    <time className="body-2">
                      {data.created_timestamp
                        ? formatDateTimeShort({
                            epochTimestamp: data.created_timestamp as number,
                          })
                        : 'N/A'}
                    </time>
                  </section>
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.LAST_UPDATED_TITLE}
                    </h3>
                    <time className="body-2">
                      {data.last_updated_timestamp
                        ? formatDateTimeShort({
                            epochTimestamp: data.last_updated_timestamp as number,
                          })
                        : 'N/A'}
                    </time>
                  </section>
                </section>
                <section className="right-panel">
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.STACK_TITLE}
                    </h3>
                    {data?.stack || 'N/A'}
                  </section>
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.CRITICALITY_TITLE}
                    </h3>
                    {data?.criticality || 'N/A'}
                  </section>
                </section>
              </section>
            </aside>
            <main className="right-panel">{this.renderTabs()}</main>
          </div>
        </div>
      );
    }

    return (
      <DocumentTitle
        title={`${this.getDisplayName()} - Amundsen Service Details`}
      >
        {innerContent}
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.service.isLoading,
  statusCode: state.service.statusCode,
  serviceData: state.service.service,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      getService,
      searchSchema: (schemaText: string) =>
        updateSearchState({
          filters: {
            [ResourceType.service]: { schema: schemaText } as any,
          },
          updateUrl: true,
        }),
    },
    dispatch
  );

export default connect<PropsFromState, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(ServiceDetail);
