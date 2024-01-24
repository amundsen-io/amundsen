// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';
import * as DocumentTitle from 'react-document-title';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { RouteComponentProps } from 'react-router';

import { GlobalState } from 'ducks/rootReducer';
import { getFileData } from 'ducks/fileMetadata/reducer';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { GetFileDataRequest } from 'ducks/fileMetadata/types';

import {
  getDescriptionSourceDisplayName,
  getMaxLength,
  getSourceIconClass,
  issueTrackingEnabled,
  notificationsEnabled,
  getTableLineageDefaultDepth,
} from 'config/config-utils';

import BadgeList from 'features/BadgeList';

import { AlertList } from 'components/Alert';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import Breadcrumb from 'features/Breadcrumb';
import EditableSection from 'components/EditableSection';
import EditableText from 'components/EditableText';
import TabsComponent, { TabInfo } from 'components/TabsComponent';
import { TAB_URL_PARAM } from 'components/TabsComponent/constants';
import TagInput from 'features/Tags/TagInput';
import LoadingSpinner from 'components/LoadingSpinner';

import { logAction, logClick } from 'utils/analytics';
import { formatDateTimeShort } from 'utils/date';
import {
  getLoggingParams,
  getUrlParam,
  setUrlParam,
  FilePageParams,
} from 'utils/navigation';

import {
  ResourceType,
  RequestMetadataType,
  FileMetadata,
} from 'interfaces';
import { FormattedDataType } from 'interfaces/ColumnList';

import TableDescEditableText from '../TableDetailPage/TableDescEditableText';
import RequestDescriptionText from '../TableDetailPage/RequestDescriptionText';
import RequestMetadataForm from '../TableDetailPage/RequestMetadataForm';

import * as Constants from './constants';
import { STATUS_CODES } from '../../constants';

import './styles.scss';


export interface PropsFromState {
  isLoading: boolean;
  statusCode: number | null;
  fileData: FileMetadata;
}
export interface DispatchFromProps {
  getFileData: (
    key: string,
    searchIndex?: string,
    source?: string
  ) => GetFileDataRequest;
}

export interface MatchProps {
  uri: string;
}

export type FileProps = PropsFromState &
  DispatchFromProps &
  RouteComponentProps<MatchProps>;

const ErrorMessage = () => (
  <div className="container error-label">
    <Breadcrumb />
    <span className="text-subtitle-w1">{Constants.ERROR_MESSAGE}</span>
  </div>
);

export interface StateProps {
  currentTab: string;
  isRightPanelOpen: boolean;
  isRightPanelPreExpanded: boolean;
  isExpandCollapseAllBtnVisible: boolean;
}

export class FilePage extends React.Component<
  FileProps & RouteComponentProps<any>,
  StateProps
> {
  private key: string;

  private didComponentMount: boolean = false;

  state = {
    currentTab: this.getDefaultTab(),
    isRightPanelOpen: false,
    isRightPanelPreExpanded: false,
    isExpandCollapseAllBtnVisible: true,
  };

  componentDidMount() {
    const defaultDepth = getTableLineageDefaultDepth();
    const {
      location,
      getFileData,
    } = this.props;
    const { index, source } = getLoggingParams(location.search);
    const {
      match: { params },
    } = this.props;

    this.key = params.uri;
    getFileData(this.key, index, source);

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
      getFileData,
      match: { params },
    } = this.props;
    const newKey = params.uri

    if (this.key !== newKey) {
      const { index, source } = getLoggingParams(location.search);

      this.key = newKey;
      getFileData(this.key, index, source);

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
    return getUrlParam(TAB_URL_PARAM) || Constants.FILE_TABS.TABLE;
  }

  getDisplayName() {
    const { match } = this.props;
    const { params } = match;

    return `${params.schema}.${params.table}`;
  }

  handleClick = (e) => {
    const { match } = this.props;
    const { params } = match;
    // const schemaText = params.schema;

    // logClick(e, {
    //   target_type: 'schema',
    //   label: schemaText,
    // });
    // searchSchema(schemaText);
  };

  preExpandRightPanel = (columnDetails: FormattedDataType) => {
    const { isRightPanelPreExpanded } = this.state;

    if (isRightPanelPreExpanded) {
      return;
    }

    let key = '';

    if (!isRightPanelPreExpanded && key) {
      this.setState({
        isRightPanelOpen: true,
        isRightPanelPreExpanded: true,
      });
    }
  };

  toggleRightPanel = (newColumnDetails: FormattedDataType | undefined) => {
    const { isRightPanelOpen } = this.state;

    let key = '';

    const shouldPanelOpen = !isRightPanelOpen;

    // if (shouldPanelOpen) {
    // }

    this.setState({
      isRightPanelOpen: shouldPanelOpen,
    });
  };

  renderTabs(editText: string, editUrl: string | null) {
    const tabInfo: TabInfo[] = [];
    const {
      fileData,
    } = this.props;
    const {
      currentTab,
      isRightPanelOpen,
    } = this.state;
    const fileParams: FilePageParams = {
      key: fileData.key,
      name: fileData.name
    };

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
            target_id: 'file_detail_tab',
            label: key,
          });
        }}
        isRightPanelOpen={isRightPanelOpen}
      />
    );
  }



  render() {
    const { isLoading, statusCode, fileData } = this.props;
    const { currentTab, isRightPanelOpen } =
      this.state;
    let innerContent: React.ReactNode;

    // We want to avoid rendering the previous table's metadata before new data is fetched in componentDidMount
    if (isLoading || !this.didComponentMount) {
      innerContent = <LoadingSpinner />;
    } else if (statusCode === STATUS_CODES.INTERNAL_SERVER_ERROR) {
      innerContent = <ErrorMessage />;
    } else {
      const data = fileData;

      innerContent = (
        <div className="resource-detail-layout table-detail">
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <span
                className={
                  'icon icon-header'
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
                resourceType={ResourceType.file}
              />
              <div className="header-details">
              </div>
              <div className="header-details">
                {data.badges && data.badges.length > 0 && <BadgeList badges={data.badges} />}
              </div>
            </div>
          </header>
          <div className="single-column-layout">
            <aside className="left-panel">
              <EditableSection
                title={Constants.DESCRIPTION_TITLE}
                readOnly={!data.is_editable}
                editText={undefined}
                editUrl={undefined}
              >
                {
                <TableDescEditableText
                  maxLength={getMaxLength('tableDescLength')}
                  value={data.description}
                  editable={data.is_editable}
                />
                 }
                <span>
                  {notificationsEnabled() && (
                    <RequestDescriptionText
                      requestMetadataType={
                        RequestMetadataType.TABLE_DESCRIPTION
                      }
                    />
                  )}
                </span>
              </EditableSection>
              {issueTrackingEnabled() && (
                <section className="metadata-section">
                  {/*
                  <TableIssues
                    tableKey={this.key}
                    tableName={this.getDisplayName()}
                  />
                */}
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
                  resourceType={ResourceType.table}
                  uriKey={fileData.key}
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
        title={`${this.getDisplayName()} - Amundsen File Details`}
      >
        {innerContent}
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.fileMetadata.isLoading,
  statusCode: state.fileMetadata.statusCode,
  fileData: state.fileMetadata.fileData,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      getFileData,
      openRequestDescriptionDialog,
    },
    dispatch
  );

export default connect<PropsFromState, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(FilePage);
