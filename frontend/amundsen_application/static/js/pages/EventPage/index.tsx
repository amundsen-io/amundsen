import * as React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import { bindActionCreators } from 'redux';
import * as DocumentTitle from 'react-document-title';
import { RouteComponentProps } from 'react-router';

import { GlobalState } from 'ducks/rootReducer';
import { getAppEvent } from 'ducks/app_event/reducer';
import { GetAppEventRequest } from 'ducks/app_event/types';

import Breadcrumb from 'components/Breadcrumb';
import LoadingSpinner from 'components/LoadingSpinner';

import * as Constants from './constants';
import { getLoggingParams } from 'utils/navigationUtils';
import { ResourceType, AppEventMetaData } from 'interfaces';

import { getSourceIconClass } from 'config/config-utils';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import TabsComponent, { TabInfo } from 'components/TabsComponent';

import './styles.scss';

import AttributeList from 'features/AttributeList';
import { formatDateTimeShort } from 'utils/dateUtils';
import { updateSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { debug } from 'console';
import SourceLink from './SourceLink';

const SERVER_ERROR_CODE = 500;

export interface PropsFromState {
  isLoading: boolean;
  statusCode: number | null;
  appEventData: AppEventMetaData;
}
export interface DispatchFromProps {
  getAppEvent: (
    key: string,
    index?: string,
    source?: string
  ) => GetAppEventRequest;
  searchSchema: (schemaText: string) => UpdateSearchStateRequest;
}

export interface MatchProps {
  key: string;
}

export type EventDetailProps = PropsFromState &
  DispatchFromProps &
  RouteComponentProps<MatchProps>;

const ErrorMessage = () => (
  <div className="container error-label">
    <Breadcrumb />
    <label>{Constants.ERROR_MESSAGE}</label>
  </div>
);

export interface StateProps {}

export class EventDetail extends React.Component<
  EventDetailProps & RouteComponentProps<any>,
  StateProps
> {
  private key: string;

  private didComponentMount: boolean = false;

  state = {
    // currentTab: this.getDefaultTab(),
  };

  componentDidMount() {
    const { location, getAppEvent } = this.props;
    const { index, source } = getLoggingParams(location.search);
    const {
      match: { params },
    } = this.props;
    this.key = params.key;
    getAppEvent(this.key, index, source);
    this.didComponentMount = true;
  }

  componentDidUpdate() {
    const {
      location,
      getAppEvent,
      match: { params },
    } = this.props;
    const newKey = params.key;
    if (this.key !== newKey) {
      const { index, source } = getLoggingParams(location.search);
      this.key = newKey;
      getAppEvent(this.key, index, source);
    }
  }

  handleClick = (e) => {
    const { match, searchSchema } = this.props;
    const { params } = match;
    const schemaText = params.schema;
    searchSchema(schemaText);
  };

  getDefaultTab() {
    return Constants.EVENT_TAB.ATTRIBUTE;
  }

  getDisplayName() {
    const { match } = this.props;
    const { params } = match;
    return params.key;
  }

  renderTabs() {
    const { appEventData } = this.props;
    const tabInfo: TabInfo[] = [
      {
        content: <AttributeList attributes={appEventData?.attributes} />,
        key: Constants.EVENT_TAB.ATTRIBUTE,
        title: `Attributes (${appEventData?.attributes?.length})`,
      },
    ];

    return (
      <TabsComponent
        tabs={tabInfo}
        defaultTab={Constants.EVENT_TAB.ATTRIBUTE}
        onSelect={(key) => {
          // this.setState({ currentTab: key });
        }}
      />
    );
    return <></>;
  }

  render() {
    let innerContent;
    const { isLoading, statusCode, appEventData } = this.props;

    if (isLoading || !this.didComponentMount) innerContent = <LoadingSpinner />;
    else if (statusCode === SERVER_ERROR_CODE) innerContent = <ErrorMessage />;
    else {
      const data = appEventData;
      innerContent = (
        <div className="resource-detail-layout event-detail">
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <span
                className={
                  'icon icon-header ' +
                  getSourceIconClass(data?.key, ResourceType.events)
                }
              />
            </div>
            <div className="header-section header-title">
              <h1 className="header-title-text truncated" title={data?.name}>
                {data?.name}
              </h1>
              <BookmarkIcon
                bookmarkKey={data?.key}
                resourceType={ResourceType.events}
              />
              <div className="body-2">
                <ul className="header-bullets">
                  <li>
                    <Link to="/search" onClick={this.handleClick}>
                      Events
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
            <div className="header-section header-links">
              {/* <SourceLink
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
              /> */}
            </div>
          </header>
          <div className="column-layout-1">
            <aside className="left-panel">
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">
                  {Constants.DESCRIPTION_TITLE}
                </h3>
                {data?.description}
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
                      {Constants.CATEGORY_TITLE}
                    </h3>

                    {data?.category || 'N/A'}
                  </section>
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.VERTICAL_TITLE}
                    </h3>
                    {data?.vertical ? (
                      <Link
                        to={`/search?resource=events&index=0&filters=%7B"vertical"%3A%7B"${data?.vertical}"%3Atrue%7D%7D`}
                      >
                        {data?.vertical}
                      </Link>
                    ) : (
                      'N/A'
                    )}
                  </section>
                </section>
                <section className="right-panel">
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.LABEL_TITLE}
                    </h3>
                    {data?.label || 'N/A'}
                  </section>
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.ACTION_TITLE}
                    </h3>
                    {data?.action || 'N/A'}
                  </section>
                  <section className="metadata-section">
                    <h3 className="section-title text-title-w3">
                      {Constants.SOURCE_TITLE}
                    </h3>
                    {data?.source ? (
                      <Link
                        to={`/search?resource=events&index=0&filters=%7B"source"%3A%7B"${data?.source}"%3Atrue%7D%7D`}
                      >
                        {data?.source}
                      </Link>
                    ) : (
                      'N/A'
                    )}
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
        title={`${this.getDisplayName()} - Amundsen Event Details`}
      >
        {innerContent}
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.event.isLoading,
  statusCode: state.event.statusCode,
  appEventData: state.event.appEvent,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      getAppEvent,
      searchSchema: (schemaText: string) =>
        updateSearchState({
          filters: {
            [ResourceType.events]: { schema: schemaText } as any,
          },
          updateUrl: true,
        }),
    },
    dispatch
  );

export default connect<PropsFromState, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(EventDetail);
