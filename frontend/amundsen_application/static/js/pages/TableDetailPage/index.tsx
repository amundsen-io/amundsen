// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';
import * as DocumentTitle from 'react-document-title';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { RouteComponentProps } from 'react-router';

import { GlobalState } from 'ducks/rootReducer';
import { getTableData } from 'ducks/tableMetadata/reducer';
import { getTableColumnLineage, getTableLineage } from 'ducks/lineage/reducer';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { updateSearchState } from 'ducks/search/reducer';
import { GetTableDataRequest } from 'ducks/tableMetadata/types';
import {
  GetTableColumnLineageRequest,
  GetTableLineageRequest,
} from 'ducks/lineage/types';
import { OpenRequestAction } from 'ducks/notification/types';
import { UpdateSearchStateRequest } from 'ducks/search/types';

import {
  getDescriptionSourceDisplayName,
  getMaxLength,
  getSourceIconClass,
  getResourceNotices,
  getTableSortCriterias,
  indexDashboardsEnabled,
  issueTrackingEnabled,
  isTableListLineageEnabled,
  notificationsEnabled,
  isTableQualityCheckEnabled,
} from 'config/config-utils';

import BadgeList from 'features/BadgeList';
import ColumnList from 'features/ColumnList';
import ColumnDetailsPanel from 'features/ColumnList/ColumnDetailsPanel';

import Alert from 'components/Alert';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import Breadcrumb from 'components/Breadcrumb';
import EditableSection from 'components/EditableSection';
import EditableText from 'components/EditableText';
import TabsComponent, { TabInfo } from 'components/TabsComponent';
import { TAB_URL_PARAM } from 'components/TabsComponent/constants';
import TagInput from 'components/Tags/TagInput';
import LoadingSpinner from 'components/LoadingSpinner';

import { logAction, logClick } from 'utils/analytics';
import { formatDateTimeShort } from 'utils/dateUtils';
import {
  buildTableKey,
  getLoggingParams,
  getUrlParam,
  setUrlParam,
  TablePageParams,
} from 'utils/navigationUtils';

import {
  ProgrammaticDescription,
  ResourceType,
  TableMetadata,
  RequestMetadataType,
  SortCriteria,
  Lineage,
  TableApp,
} from 'interfaces';
import { FormattedDataType } from 'interfaces/ColumnList';

import DataPreviewButton from './DataPreviewButton';
import ExploreButton from './ExploreButton';
import LineageButton from './LineageButton';
import FrequentUsers from './FrequentUsers';
import LineageLink from './LineageLink';
import LineageList from './LineageList';
import TableOwnerEditor from './TableOwnerEditor';
import SourceLink from './SourceLink';
import TableDashboardResourceList from './TableDashboardResourceList';
import TableDescEditableText from './TableDescEditableText';
import TableHeaderBullets from './TableHeaderBullets';
import TableIssues from './TableIssues';
import WatermarkLabel from './WatermarkLabel';
import ApplicationDropdown from './ApplicationDropdown';
import TableQualityChecksLabel from './TableQualityChecks';
import TableReportsDropdown from './ResourceReportsDropdown';
import RequestDescriptionText from './RequestDescriptionText';
import RequestMetadataForm from './RequestMetadataForm';
import ListSortingDropdown from './ListSortingDropdown';

import * as Constants from './constants';
import { AIRFLOW, DATABRICKS } from './ApplicationDropdown/constants';

import './styles.scss';

const SERVER_ERROR_CODE = 500;
const DASHBOARDS_PER_PAGE = 10;
const TABLE_SOURCE = 'table_page';
const SORT_CRITERIAS = {
  ...getTableSortCriterias(),
};

export interface PropsFromState {
  isLoading: boolean;
  isLoadingDashboards: boolean;
  numRelatedDashboards: number;
  statusCode: number | null;
  tableData: TableMetadata;
  tableLineage: Lineage;
}
export interface DispatchFromProps {
  getTableData: (
    key: string,
    searchIndex?: string,
    source?: string
  ) => GetTableDataRequest;
  getTableLineageDispatch: (key: string) => GetTableLineageRequest;
  getColumnLineageDispatch: (
    key: string,
    columnName: string
  ) => GetTableColumnLineageRequest;
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName: string
  ) => OpenRequestAction;
  searchSchema: (schemaText: string) => UpdateSearchStateRequest;
}

export interface MatchProps {
  cluster: string;
  database: string;
  schema: string;
  table: string;
}

export type TableDetailProps = PropsFromState &
  DispatchFromProps &
  RouteComponentProps<MatchProps>;

const ErrorMessage = () => (
  <div className="container error-label">
    <Breadcrumb />
    <label>{Constants.ERROR_MESSAGE}</label>
  </div>
);

export interface StateProps {
  areNestedColumnsExpanded: boolean | undefined;
  sortedBy: SortCriteria;
  currentTab: string;
  isRightPanelOpen: boolean;
  isRightPanelPreExpanded: boolean;
  isExpandCollapseAllBtnVisible: boolean;
  selectedColumnKey: string;
  selectedColumnDetails?: FormattedDataType;
}

export class TableDetail extends React.Component<
  TableDetailProps & RouteComponentProps<any>,
  StateProps
> {
  private key: string;

  private didComponentMount: boolean = false;

  state = {
    areNestedColumnsExpanded: undefined,
    sortedBy: SORT_CRITERIAS.sort_order,
    currentTab: this.getDefaultTab(),
    isRightPanelOpen: false,
    isRightPanelPreExpanded: false,
    isExpandCollapseAllBtnVisible: true,
    selectedColumnKey: '',
    selectedColumnDetails: undefined,
  };

  componentDidMount() {
    const { location, getTableData, getTableLineageDispatch } = this.props;
    const { index, source } = getLoggingParams(location.search);
    const {
      match: { params },
    } = this.props;
    this.key = buildTableKey(params);
    getTableData(this.key, index, source);

    if (isTableListLineageEnabled()) {
      getTableLineageDispatch(this.key);
    }
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
      getTableData,
      getTableLineageDispatch,
      match: { params },
    } = this.props;
    const newKey = buildTableKey(params);

    if (this.key !== newKey) {
      const { index, source } = getLoggingParams(location.search);

      this.key = newKey;
      getTableData(this.key, index, source);

      if (isTableListLineageEnabled()) {
        getTableLineageDispatch(this.key);
      }
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

  handleEscKey = (event) => {
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
    return getUrlParam(TAB_URL_PARAM) || Constants.TABLE_TAB.COLUMN;
  }

  getDisplayName() {
    const { match } = this.props;
    const { params } = match;

    return `${params.schema}.${params.table}`;
  }

  handleClick = (e) => {
    const { match, searchSchema } = this.props;
    const { params } = match;
    const schemaText = params.schema;

    logClick(e, {
      target_type: 'schema',
      label: schemaText,
    });
    searchSchema(schemaText);
  };

  renderProgrammaticDesc = (
    descriptions: ProgrammaticDescription[] | undefined
  ) => {
    if (!descriptions) {
      return null;
    }

    return descriptions.map((d) => (
      <EditableSection key={`prog_desc:${d.source}`} title={d.source} readOnly>
        <EditableText
          maxLength={999999}
          value={d.text}
          editable={false}
          allowDangerousHtml
        />
      </EditableSection>
    ));
  };

  toggleExpandingColumns = () => {
    const { areNestedColumnsExpanded } = this.state;
    const newValue =
      areNestedColumnsExpanded !== undefined
        ? !areNestedColumnsExpanded
        : false;

    this.setState({ areNestedColumnsExpanded: newValue });
  };

  handleSortingChange = (sortValue) => {
    this.toggleSort(SORT_CRITERIAS[sortValue]);
  };

  toggleSort = (sorting: SortCriteria) => {
    const { sortedBy } = this.state;

    if (sorting !== sortedBy) {
      this.setState({
        sortedBy: sorting,
      });
    }
  };

  preExpandRightPanel = (columnDetails: FormattedDataType) => {
    const { isRightPanelPreExpanded } = this.state;
    const { getColumnLineageDispatch } = this.props;

    if (isRightPanelPreExpanded) {
      return;
    }

    let key = '';
    if (columnDetails) {
      ({ key } = columnDetails);
      if (!columnDetails.isNestedColumn) {
        const { name, tableParams } = columnDetails;
        getColumnLineageDispatch(buildTableKey(tableParams), name);
      }
    }

    if (!isRightPanelPreExpanded && key) {
      this.setState({
        isRightPanelOpen: true,
        isRightPanelPreExpanded: true,
        selectedColumnKey: key,
        selectedColumnDetails: columnDetails,
      });
    }
  };

  toggleRightPanel = (newColumnDetails: FormattedDataType | undefined) => {
    const { isRightPanelOpen, selectedColumnKey } = this.state;
    const { getColumnLineageDispatch } = this.props;

    let key = '';
    if (newColumnDetails) {
      ({ key } = newColumnDetails);
    }

    const shouldPanelOpen =
      (key && key !== selectedColumnKey) || !isRightPanelOpen;

    if (
      shouldPanelOpen &&
      newColumnDetails &&
      !newColumnDetails.isNestedColumn
    ) {
      const { name, tableParams } = newColumnDetails;
      getColumnLineageDispatch(buildTableKey(tableParams), name);
    }

    if (newColumnDetails && shouldPanelOpen) {
      logAction({
        command: 'click',
        label: `${newColumnDetails.key} ${newColumnDetails.type.type}`,
        target_id: `column::${newColumnDetails.key}`,
        target_type: 'column stats',
      });
    }

    this.setState({
      isRightPanelOpen: shouldPanelOpen,
      selectedColumnKey: shouldPanelOpen ? key : '',
      selectedColumnDetails: newColumnDetails,
    });
  };

  hasColumnsToExpand = () => {
    const { tableData } = this.props;
    return tableData.columns.some((col) => col.type_metadata?.children?.length);
  };

  renderTabs(editText, editUrl) {
    const tabInfo: TabInfo[] = [];
    const {
      isLoadingDashboards,
      numRelatedDashboards,
      tableData,
      tableLineage,
    } = this.props;
    const {
      areNestedColumnsExpanded,
      sortedBy,
      currentTab,
      isRightPanelOpen,
      selectedColumnKey,
    } = this.state;
    const tableParams: TablePageParams = {
      cluster: tableData.cluster,
      database: tableData.database,
      table: tableData.name,
      schema: tableData.schema,
    };
    const selectedColumn = getUrlParam(Constants.COLUMN_URL_KEY);

    // Default Column content
    tabInfo.push({
      content: (
        <ColumnList
          columns={tableData.columns}
          database={tableData.database}
          tableParams={tableParams}
          editText={editText}
          editUrl={editUrl}
          sortBy={sortedBy}
          preExpandPanelKey={
            selectedColumn ? tableData.key + '/' + selectedColumn : undefined
          }
          preExpandRightPanel={this.preExpandRightPanel}
          hideSomeColumnMetadata={isRightPanelOpen}
          toggleRightPanel={this.toggleRightPanel}
          currentSelectedKey={selectedColumnKey}
          areNestedColumnsExpanded={areNestedColumnsExpanded}
          toggleExpandingColumns={this.toggleExpandingColumns}
          hasColumnsToExpand={this.hasColumnsToExpand}
        />
      ),
      key: Constants.TABLE_TAB.COLUMN,
      title: `Columns (${tableData.columns.length})`,
    });

    if (indexDashboardsEnabled()) {
      const loadingTitle = (
        <div className="tab-title">
          Dashboards <LoadingSpinner />
        </div>
      );

      tabInfo.push({
        content: (
          <TableDashboardResourceList
            itemsPerPage={DASHBOARDS_PER_PAGE}
            source={TABLE_SOURCE}
          />
        ),
        key: Constants.TABLE_TAB.DASHBOARD,
        title: isLoadingDashboards
          ? loadingTitle
          : `Dashboards (${numRelatedDashboards})`,
      });
    }

    if (isTableListLineageEnabled()) {
      if (tableLineage.upstream_entities.length > 0) {
        tabInfo.push({
          content: (
            <LineageList
              items={tableLineage.upstream_entities}
              direction="upstream"
            />
          ),
          key: Constants.TABLE_TAB.UPSTREAM,
          title: `Upstream (${tableLineage.upstream_entities.length})`,
        });
      }
      if (tableLineage.downstream_entities.length > 0) {
        tabInfo.push({
          content: (
            <LineageList
              items={tableLineage.downstream_entities}
              direction="downstream"
            />
          ),
          key: Constants.TABLE_TAB.DOWNSTREAM,
          title: `Downstream (${tableLineage.downstream_entities.length})`,
        });
      }
    }

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
            target_id: 'table_detail_tab',
            label: key,
          });
        }}
        isRightPanelOpen={isRightPanelOpen}
      />
    );
  }

  renderColumnTabActionButtons(isRightPanelOpen, sortedBy) {
    const {
      areNestedColumnsExpanded,
      isExpandCollapseAllBtnVisible,
    } = this.state;

    return (
      <div
        className={`column-tab-action-buttons ${
          isRightPanelOpen ? 'has-open-right-panel' : 'has-closed-right-panel'
        }`}
      >
        {isExpandCollapseAllBtnVisible && this.hasColumnsToExpand() && (
          <button
            className="btn btn-link expand-collapse-all-button"
            type="button"
            onClick={this.toggleExpandingColumns}
          >
            <h3 className="expand-collapse-all-text">
              {areNestedColumnsExpanded ||
              areNestedColumnsExpanded === undefined
                ? Constants.COLLAPSE_ALL_NESTED_LABEL
                : Constants.EXPAND_ALL_NESTED_LABEL}
            </h3>
          </button>
        )}
        {!isRightPanelOpen && (
          <ListSortingDropdown
            options={SORT_CRITERIAS}
            currentSelection={sortedBy}
            onChange={this.handleSortingChange}
          />
        )}
      </div>
    );
  }

  renderTableAppDropdowns(tableWriter, tableApps) {
    let apps: TableApp[] = [];

    const hasNoAppsOrWriter =
      (tableApps === null || tableApps.length === 0) && tableWriter === null;
    if (hasNoAppsOrWriter) {
      return null;
    }
    const hasNonEmptyTableApps = tableApps !== null && tableApps.length > 0;
    if (hasNonEmptyTableApps) {
      apps = [...tableApps];
    }
    const hasWriterWithUniqueId =
      tableWriter !== null && !apps.some((app) => app.id === tableWriter.id);
    if (hasWriterWithUniqueId) {
      apps = [...apps, tableWriter];
    }

    const airflowApps = apps.filter(
      (app) => app.name.toLowerCase() === AIRFLOW.toLowerCase()
    );
    const databricksApps = apps.filter(
      (app) => app.name.toLowerCase() === DATABRICKS.toLowerCase()
    );
    const remainingApps = apps.filter(
      (app) =>
        app.name.toLowerCase() !== AIRFLOW.toLowerCase() &&
        app.name.toLowerCase() !== DATABRICKS.toLowerCase()
    );

    return (
      <div>
        {airflowApps.length > 0 && (
          <ApplicationDropdown tableApps={airflowApps} />
        )}
        {databricksApps.length > 0 && (
          <ApplicationDropdown tableApps={databricksApps} />
        )}
        {remainingApps.length > 0 && (
          <ApplicationDropdown tableApps={remainingApps} />
        )}
      </div>
    );
  }

  render() {
    const { isLoading, statusCode, tableData } = this.props;
    const {
      sortedBy,
      currentTab,
      isRightPanelOpen,
      selectedColumnDetails,
    } = this.state;
    let innerContent;

    // We want to avoid rendering the previous table's metadata before new data is fetched in componentDidMount
    if (isLoading || !this.didComponentMount) {
      innerContent = <LoadingSpinner />;
    } else if (statusCode === SERVER_ERROR_CODE) {
      innerContent = <ErrorMessage />;
    } else {
      const data = tableData;
      const editText = data.source
        ? `${Constants.EDIT_DESC_TEXT} ${getDescriptionSourceDisplayName(
            data.source.source_type
          )}`
        : '';
      const ownersEditText = data.source
        ? // TODO rename getDescriptionSourceDisplayName to more generic since
          // owners also edited on the same file?
          `${Constants.EDIT_OWNERS_TEXT} ${getDescriptionSourceDisplayName(
            data.source.source_type
          )}`
        : '';
      const editUrl = data.source ? data.source.source : '';
      const tableNotice = getResourceNotices(
        ResourceType.table,
        `${data.cluster}.${data.database}.${data.schema}.${data.name}`
      );

      innerContent = (
        <div className="resource-detail-layout table-detail">
          {notificationsEnabled() && <RequestMetadataForm />}
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <span
                className={
                  'icon icon-header ' +
                  getSourceIconClass(data.database, ResourceType.table)
                }
              />
            </div>
            <div className="header-section header-title">
              <h1
                className="header-title-text truncated"
                title={`${data.schema}.${data.name}`}
              >
                <Link to="/search" onClick={this.handleClick}>
                  {data.schema}
                </Link>
                .{data.name}
              </h1>
              <BookmarkIcon
                bookmarkKey={data.key}
                resourceType={ResourceType.table}
              />
              <div className="header-details">
                <TableHeaderBullets
                  database={data.database}
                  cluster={data.cluster}
                  isView={data.is_view}
                />
                {data.badges.length > 0 && <BadgeList badges={data.badges} />}
              </div>
            </div>
            <div className="header-section header-links header-external-links">
              {this.renderTableAppDropdowns(data.table_writer, data.table_apps)}
              <LineageLink tableData={data} />
              <SourceLink tableSource={data.source} />
            </div>
            <div className="header-section header-buttons">
              <LineageButton tableData={data} />
              <TableReportsDropdown resourceReports={data.resource_reports} />
              <DataPreviewButton modalTitle={this.getDisplayName()} />
              <ExploreButton tableData={data} />
            </div>
          </header>
          <div className="single-column-layout">
            <aside className="left-panel">
              {!!tableNotice && (
                <Alert
                  message={tableNotice.messageHtml}
                  severity={tableNotice.severity}
                />
              )}
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
                  <TableIssues
                    tableKey={this.key}
                    tableName={this.getDisplayName()}
                  />
                </section>
              )}
              <section className="two-column-layout">
                <section className="left-column">
                  {!!data.last_updated_timestamp && (
                    <section className="metadata-section">
                      <div className="section-title">
                        {Constants.LAST_UPDATED_TITLE}
                      </div>
                      <time className="time-body-text">
                        {formatDateTimeShort({
                          epochTimestamp: data.last_updated_timestamp,
                        })}
                      </time>
                    </section>
                  )}
                  <section className="metadata-section">
                    <div className="section-title">
                      {Constants.DATE_RANGE_TITLE}
                    </div>
                    <WatermarkLabel watermarks={data.watermarks} />
                  </section>
                  <EditableSection title={Constants.TAG_TITLE}>
                    <TagInput
                      resourceType={ResourceType.table}
                      uriKey={tableData.key}
                    />
                  </EditableSection>
                  {isTableQualityCheckEnabled() && (
                    <TableQualityChecksLabel tableKey={tableData.key} />
                  )}
                  {this.renderProgrammaticDesc(
                    data.programmatic_descriptions.left
                  )}
                </section>
                <section className="right-column">
                  <EditableSection
                    title={Constants.OWNERS_TITLE}
                    readOnly={!data.is_editable}
                    editText={ownersEditText}
                    editUrl={editUrl || undefined}
                  >
                    <TableOwnerEditor resourceType={ResourceType.table} />
                  </EditableSection>
                  <section className="metadata-section">
                    <div className="section-title">
                      {Constants.FREQ_USERS_TITLE}
                    </div>
                    <FrequentUsers readers={data.table_readers} />
                  </section>
                  {this.renderProgrammaticDesc(
                    data.programmatic_descriptions.right
                  )}
                </section>
              </section>
              {this.renderProgrammaticDesc(
                data.programmatic_descriptions.other
              )}
            </aside>
            <main className="main-content-panel">
              {currentTab === Constants.TABLE_TAB.COLUMN &&
                this.renderColumnTabActionButtons(isRightPanelOpen, sortedBy)}
              {this.renderTabs(editText, editUrl)}
            </main>
            {isRightPanelOpen && selectedColumnDetails && (
              <ColumnDetailsPanel
                columnDetails={selectedColumnDetails!}
                togglePanel={this.toggleRightPanel}
              />
            )}
          </div>
        </div>
      );
    }

    return (
      <DocumentTitle
        title={`${this.getDisplayName()} - Amundsen Table Details`}
      >
        {innerContent}
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.tableMetadata.isLoading,
  statusCode: state.tableMetadata.statusCode,
  tableData: state.tableMetadata.tableData,
  tableLineage: state.lineage.lineageTree,
  numRelatedDashboards: state.tableMetadata.dashboards
    ? state.tableMetadata.dashboards.dashboards.length
    : 0,
  isLoadingDashboards: state.tableMetadata.dashboards
    ? state.tableMetadata.dashboards.isLoading
    : true,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      getTableData,
      getTableLineageDispatch: getTableLineage,
      getColumnLineageDispatch: getTableColumnLineage,
      openRequestDescriptionDialog,
      searchSchema: (schemaText: string) =>
        updateSearchState({
          filters: {
            [ResourceType.table]: { schema: { value: schemaText } },
          },
          submitSearch: true,
        }),
    },
    dispatch
  );

export default connect<PropsFromState, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(TableDetail);
