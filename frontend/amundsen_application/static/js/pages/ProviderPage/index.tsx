// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';
import * as DocumentTitle from 'react-document-title';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { RouteComponentProps } from 'react-router';

import { GlobalState } from 'ducks/rootReducer';
import { getProviderData } from 'ducks/providerMetadata/reducer';
import { getNotices } from 'ducks/notices';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { GetProviderDataRequest } from 'ducks/providerMetadata/types';
import { OpenRequestAction } from 'ducks/notification/types';

import {
  getMaxLength,
  getSourceIconClass,
  getResourceNotices,
  issueTrackingEnabled,
  notificationsEnabled,
} from 'config/config-utils';
import { NoticeType, NoticeSeverity } from 'config/config-types';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import Breadcrumb from 'features/Breadcrumb';
import EditableSection from 'components/EditableSection';
import TabsComponent, { TabInfo } from 'components/TabsComponent';
import { TAB_URL_PARAM } from 'components/TabsComponent/constants';
import TagInput from 'features/Tags/TagInput';
import LoadingSpinner from 'components/LoadingSpinner';

import { logAction, logClick } from 'utils/analytics';
import {
  buildProviderKey,
  getLoggingParams,
  getUrlParam,
  setUrlParam,
  ProviderPageParams,
} from 'utils/navigation';

import {
  ResourceType,
  ProviderMetadata,
  RequestMetadataType,
  DynamicResourceNotice,
} from 'interfaces';
import { FormattedDataType } from 'interfaces/ColumnList';

import ProviderHeaderBullets from './ProviderHeaderBullets';

import TableDescEditableText from '../TableDetailPage/TableDescEditableText';
import RequestMetadataForm from '../TableDetailPage/RequestMetadataForm';

import * as Constants from './constants';
import { STATUS_CODES } from '../../constants';

import './styles.scss';

const DASHBOARDS_PER_PAGE = 10;
const PROVIDER_SOURCE = 'provider_page';
const SEVERITY_TO_NOTICE_SEVERITY = {
  0: NoticeSeverity.INFO,
  1: NoticeSeverity.WARNING,
  2: NoticeSeverity.ALERT,
};

/**
 * Merges the dynamic and static notices, doing a type matching for dynamic ones
 * @param data            Table metadata
 * @param notices         Dynamic notices
 * @returns NoticeType[]  Aggregated notices
 */
const aggregateResourceNotices = (
  data: ProviderMetadata,
  notices: DynamicResourceNotice[]
): NoticeType[] => {
  const staticNotice = getResourceNotices(
    ResourceType.table,
    `${data.name}`
  );
  const dynamicNotices: NoticeType[] = notices.map((notice) => ({
    severity: SEVERITY_TO_NOTICE_SEVERITY[notice.severity],
    messageHtml: notice.message,
    payload: notice.payload,
  }));

  return staticNotice ? [...dynamicNotices, staticNotice] : dynamicNotices;
};

export interface PropsFromState {
  isLoading: boolean;
  statusCode: number | null;
  providerData: ProviderMetadata;
}
export interface DispatchFromProps {
  getProviderData: (
    key: string,
    searchIndex?: string,
    source?: string
  ) => GetProviderDataRequest;
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName: string
  ) => OpenRequestAction;
}

export interface MatchProps {
  name: string;
}

export type ProviderProps = PropsFromState &
  DispatchFromProps &
  RouteComponentProps<MatchProps>;

const ErrorMessage = () => (
  <div className="container error-label">
    <Breadcrumb />
    <span className="text-subtitle-w1">{Constants.ERROR_MESSAGE}</span>
  </div>
);

export interface StateProps {
  areNestedColumnsExpanded: boolean | undefined;
  currentTab: string;
  isRightPanelOpen: boolean;
  isRightPanelPreExpanded: boolean;
  isExpandCollapseAllBtnVisible: boolean;
}

export class ProviderPage extends React.Component<
  ProviderProps & RouteComponentProps<any>,
  StateProps
> {
  private key: string;

  private didComponentMount: boolean = false;

  state = {
    areNestedColumnsExpanded: undefined,
    currentTab: this.getDefaultTab(),
    isRightPanelOpen: false,
    isRightPanelPreExpanded: false,
    isExpandCollapseAllBtnVisible: true,
  };

  componentDidMount() {
    const {
      location,
      getProviderData,
    } = this.props;
    const { index, source } = getLoggingParams(location.search);
    const {
      match: { params },
    } = this.props;

    this.key = buildProviderKey(params);
    getProviderData(this.key, index, source);

    document.addEventListener('keydown', this.handleEscKey);
    window.addEventListener(
      'resize',
      this.handleExpandCollapseAllBtnVisibility
    );
    this.didComponentMount = true;
  }

  componentDidUpdate() {
    const {
      location,
      getProviderData,
      match: { params },
    } = this.props;
    const newKey = buildProviderKey(params);

    if (this.key !== newKey) {
      const { index, source } = getLoggingParams(location.search);

      this.key = newKey;
      getProviderData(this.key, index, source);

      // eslint-disable-next-line react/no-did-update-set-state
      this.setState({ currentTab: this.getDefaultTab() });
    }
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleEscKey);
    window.removeEventListener(
      'resize',
      this.handleExpandCollapseAllBtnVisibility
    );
  }

  handleEscKey = (event: KeyboardEvent) => {
    const { isRightPanelOpen } = this.state;

    if (event.key === Constants.ESC_BUTTON_KEY && isRightPanelOpen) {
      this.toggleRightPanel(undefined);
    }
  };

  handleExpandCollapseAllBtnVisibility = () => {
    const { isRightPanelOpen } = this.state;
    const minWidth = isRightPanelOpen
      ? Constants.MIN_WIDTH_DISPLAY_BTN_WITH_OPEN_PANEL
      : Constants.MIN_WIDTH_DISPLAY_BTN;
    let newState = { isExpandCollapseAllBtnVisible: false };

    if (window.matchMedia(`(min-width: ${minWidth}px)`).matches) {
      newState = { isExpandCollapseAllBtnVisible: true };
    }
    this.setState(newState);
  };

  getDefaultTab() {
    return getUrlParam(TAB_URL_PARAM) || Constants.PROVIDER_TABS.DASHBOARD;
  }

  getDisplayName() {
    const { match } = this.props;
    const { params } = match;

    return `${params.name}`;
  }

  handleClick = (e) => {
    const { match } = this.props;
    const { params } = match;
    const schemaText = params.schema;

    logClick(e, {
      target_type: 'schema',
      label: schemaText,
    });
  };

  toggleExpandingColumns = () => {
    const { areNestedColumnsExpanded } = this.state;
    const newValue =
      areNestedColumnsExpanded !== undefined
        ? !areNestedColumnsExpanded
        : false;

    this.setState({ areNestedColumnsExpanded: newValue });
  };

  preExpandRightPanel = (columnDetails: FormattedDataType) => {
    const { isRightPanelPreExpanded } = this.state;
    const { } = this.props;

    if (isRightPanelPreExpanded) {
      return;
    }

    let key = '';

    if (columnDetails) {
      ({ key } = columnDetails);
    }

    if (!isRightPanelPreExpanded && key) {
      this.setState({
        isRightPanelOpen: true,
        isRightPanelPreExpanded: true,
      });
    }
  };

  toggleRightPanel = (newColumnDetails: FormattedDataType | undefined) => {
    const { isRightPanelOpen } = this.state;
    const { } = this.props;

    const shouldPanelOpen = !isRightPanelOpen;

    if (shouldPanelOpen) {
      // logAction({
      //   command: 'click',
      //   label: `${newColumnDetails.key} ${newColumnDetails.type.type}`,
      //   target_id: `column::${newColumnDetails.key}`,
      //   target_type: 'column stats',
      // });
    }

    this.setState({
      isRightPanelOpen: shouldPanelOpen,
    });
  };

  hasColumnsToExpand = () => {
    const { providerData } = this.props;

    return false;
  };

  renderTabs(editText: string, editUrl: string | null) {
    const tabInfo: TabInfo[] = [];
    const {
      providerData,
    } = this.props;
    const {
      currentTab,
      isRightPanelOpen,
    } = this.state;

    return (
      <TabsComponent
        tabs={tabInfo}
        defaultTab={currentTab}
        onSelect={(key) => {
          if (isRightPanelOpen) {
            this.toggleRightPanel(undefined);
          }
          this.setState({ currentTab: key });
          setUrlParam(TAB_URL_PARAM, key);
          logAction({
            command: 'click',
            target_id: 'provider_detail_tab',
            label: key,
          });
        }}
        isRightPanelOpen={isRightPanelOpen}
      />
    );
  }

  render() {
    const { isLoading, statusCode, providerData } = this.props;
    const { currentTab, isRightPanelOpen } =
      this.state;
    let innerContent: React.ReactNode;

    // We want to avoid rendering the previous table's metadata before new data is fetched in componentDidMount
    if (isLoading || !this.didComponentMount) {
      innerContent = <LoadingSpinner />;
    } else if (statusCode === STATUS_CODES.INTERNAL_SERVER_ERROR) {
      innerContent = <ErrorMessage />;
    } else {
      const data = providerData;
      const editText = '';
      const editUrl = '';

      innerContent = (
        <div className="resource-detail-layout table-detail">
          {notificationsEnabled() && <RequestMetadataForm />}
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <span
                className={
                  'icon icon-header ' +
                  getSourceIconClass(data.name, ResourceType.data_provider)
                }
              />
            </div>
            <div className="header-section header-title">
              <h1
                className="header-title-text truncated"
                title={`${data.name}`}
              >
                {data.name}
              </h1>
              <BookmarkIcon
                bookmarkKey={data.key}
                resourceType={ResourceType.data_provider}
              />
              <div className="header-details">
                <ProviderHeaderBullets
                  name={data.name}
                />
              </div>
              <div className="header-details">
              </div>
            </div>
          </header>
          <div className="single-column-layout">
            <aside className="left-panel">
              <EditableSection
                title={Constants.DESCRIPTION_TITLE}
                readOnly={!data.is_editable}
                editText={editText}
                editUrl={editUrl || undefined}
              >
                <TableDescEditableText
                  maxLength={getMaxLength('tableDescLength')}
                  value={data.description}
                  editable={data.is_editable}
                />
                <span>
                </span>
              </EditableSection>
              {issueTrackingEnabled() && (
                <section className="metadata-section">
                  {/* <TableIssues
                    tableKey={this.key}
                    tableName={this.getDisplayName()}
                  /> */}
                </section>
              )}
              <section className="two-column-layout">
                <section className="left-column">
                  <section className="metadata-section">
                    <div className="section-title">
                      {Constants.LAST_UPDATED_TITLE}
                    </div>
                  </section>
                  <section className="metadata-section">
                    <div className="section-title">
                      {Constants.DATE_RANGE_TITLE}
                    </div>
                  </section>
                </section>
                <section className="right-column">
                </section>
              </section>
              <EditableSection title={Constants.TAG_TITLE}>
                <TagInput
                  resourceType={ResourceType.data_provider}
                  uriKey={providerData.key}
                />
              </EditableSection>
            </aside>
            <main className="main-content-panel">
            </main>
          </div>
        </div>
      );
    }

    return (
      <DocumentTitle
        title={`${this.getDisplayName()} - Amundsen Data Provider Details`}
      >
        {innerContent}
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.providerMetadata.isLoading,
  statusCode: state.providerMetadata.statusCode,
  providerData: state.providerMetadata.providerData,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      getProviderData,
      getNoticesDispatch: getNotices,
      openRequestDescriptionDialog,
    },
    dispatch
  );

export default connect<PropsFromState, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(ProviderPage);
