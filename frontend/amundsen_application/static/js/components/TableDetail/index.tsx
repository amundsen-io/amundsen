import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { RouteComponentProps } from 'react-router';

import { GlobalState } from 'ducks/rootReducer';
import { getTableData } from 'ducks/tableMetadata/reducer';
import { GetTableDataRequest } from 'ducks/tableMetadata/types';

import AppConfig from 'config/config';
import BadgeList from 'components/common/BadgeList';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import Breadcrumb from 'components/common/Breadcrumb';
import TabsComponent from 'components/common/TabsComponent';
import EditableText from 'components/common/EditableText';
import LoadingSpinner from 'components/common/LoadingSpinner';
import Flag from 'components/common/Flag';
import ResourceList from 'components/common/ResourceList';

import DataPreviewButton from 'components/TableDetail/DataPreviewButton';
import ColumnList from 'components/TableDetail/ColumnList';
import ExploreButton from 'components/TableDetail/ExploreButton';
import FrequentUsers from 'components/TableDetail/FrequentUsers';
import LineageLink from 'components/TableDetail/LineageLink';
import OwnerEditor from 'components/TableDetail/OwnerEditor';
import SourceLink from 'components/TableDetail/SourceLink';
import TableDescEditableText from 'components/TableDetail/TableDescEditableText';
import TableHeaderBullets from 'components/TableDetail/TableHeaderBullets';
import TableIssues from 'components/TableDetail/TableIssues';
import WatermarkLabel from 'components/TableDetail/WatermarkLabel';
import WriterLink from 'components/TableDetail/WriterLink';
import TagInput from 'components/Tags/TagInput';
import { ResourceType, TableMetadata} from 'interfaces';

import EditableSection from 'components/common/EditableSection';

import { getSourceIconClass, issueTrackingEnabled, notificationsEnabled } from 'config/config-utils';

import { formatDateTimeShort } from 'utils/dateUtils';
import { getLoggingParams } from 'utils/logUtils';

import RequestDescriptionText from './RequestDescriptionText';
import RequestMetadataForm from './RequestMetadataForm';

import { PROGRMMATIC_DESC_HEADER, ERROR_MESSAGE } from './constants';

import './styles.scss';

const SERVER_ERROR_CODE = 500;
const DASHBOARDS_PER_PAGE = 10;
const TABLE_SOURCE = "table_page";

export interface StateFromProps {
  isLoading: boolean;
  statusCode?: number;
  tableData: TableMetadata;
}
export interface DispatchFromProps {
  getTableData: (key: string, searchIndex?: string, source?: string, ) => GetTableDataRequest;
}
export interface MatchProps {
  cluster: string;
  database: string;
  schema: string;
  table: string;
}
export type TableDetailProps = StateFromProps & DispatchFromProps & RouteComponentProps<MatchProps>;

const ErrorMessage = () => {
  return (
    <div className="container error-label">
      <Breadcrumb />
      <label>{ERROR_MESSAGE}</label>
    </div>
  );
};

export class TableDetail extends React.Component<TableDetailProps & RouteComponentProps<any>> {
  private key: string;
  private didComponentMount: boolean = false;

  componentDidMount() {
    const { index, source } = getLoggingParams(this.props.location.search);

    this.key = this.getTableKey();
    this.props.getTableData(this.key, index, source);
    this.didComponentMount = true;
  }

  componentDidUpdate() {
    const newKey = this.getTableKey();

    if (this.key !== newKey) {
      const { index, source } = getLoggingParams(this.props.location.search);
      this.key = newKey;
      this.props.getTableData(this.key, index, source);
    }
  }

  getDisplayName() {
    const params = this.props.match.params;

    return `${params.schema}.${params.table}`;
  }

  getTableKey() {
    /*
    This 'key' is the `table_uri` format described in metadataservice. Because it contains the '/' character,
    we can't pass it as a single URL parameter without encodeURIComponent which makes ugly URLs.
    DO NOT CHANGE
    */
    const params = this.props.match.params;

    return `${params.database}://${params.cluster}.${params.schema}/${params.table}`;
  }

  renderTabs() {
    const tabInfo = [];

    // Default Column content
    tabInfo.push({
      content:
        (
          <ColumnList columns={ this.props.tableData.columns }/>
        ),
      key: 'columns',
      title: `Columns (${this.props.tableData.columns.length})`,
    });

    // Dashboard content
    tabInfo.push({
      content: (
        <ResourceList
          allItems={this.props.tableData.dashboards}
          itemsPerPage={DASHBOARDS_PER_PAGE}
          source={TABLE_SOURCE}
        />
      ),
      key: "dashboards",
      title: `Dashboards (${this.props.tableData.dashboards.length})`
    });

    return <TabsComponent tabs={ tabInfo } defaultTab={ "columns" } />;
  }

  render() {
    const {isLoading, statusCode, tableData} = this.props;
    let innerContent;

    // We want to avoid rendering the previous table's metadata before new data is fetched in componentDidMount
    if (isLoading || !this.didComponentMount) {
      innerContent = <LoadingSpinner/>;
    } else if (statusCode === SERVER_ERROR_CODE) {
      innerContent = (<ErrorMessage />);
    } else {
      const data = tableData;

      innerContent = (
        <div className="resource-detail-layout table-detail">
          {
            notificationsEnabled() && <RequestMetadataForm />
          }
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <span className={"icon icon-header " + getSourceIconClass(data.database, ResourceType.table)} />
            </div>
            <div className="header-section header-title">
              <h3 className="header-title-text truncated">
                  { this.getDisplayName() }
              </h3>
              <BookmarkIcon bookmarkKey={ data.key } resourceType={ ResourceType.table } />
              <div className="body-2">
                <TableHeaderBullets
                  database={ data.database }
                  cluster={ data.cluster }
                />
                {
                  data.badges.length > 0 &&
                  <BadgeList badges={ data.badges } />
                }
                {
                  data.is_view &&
                  <Flag text="table view" labelStyle="warning"/>
                }
              </div>
            </div>
            <div className="header-section header-links">
              <WriterLink tableWriter={ data.table_writer }/>
              <LineageLink tableData={ data }/>
              <SourceLink tableSource={ data.source }/>
            </div>
            <div className="header-section header-buttons">
              <DataPreviewButton modalTitle={ this.getDisplayName() }/>
              <ExploreButton tableData={ data }/>
            </div>
          </header>
          <article className="column-layout-1">
            <section className="left-panel">
              <EditableSection title="Description">
                <TableDescEditableText
                  maxLength={ AppConfig.editableText.tableDescLength }
                  value={ data.description }
                  editable={ data.is_editable }
                />
                <span>
                  { notificationsEnabled() && <RequestDescriptionText/> }
                </span>
              </EditableSection>
              {
                issueTrackingEnabled() &&
                <section className="metadata-section">
                  <TableIssues tableKey={ this.key } tableName={ this.getDisplayName()}/>
                </section>
              }
              <section className="column-layout-2">
                <section className="left-panel">
                  {
                    !data.is_view &&
                    <section className="metadata-section">
                      <div className="section-title title-3">Date Range</div>
                      <WatermarkLabel watermarks={ data.watermarks }/>
                    </section>
                  }
                  {
                    !!data.last_updated_timestamp &&
                    <section className="metadata-section">
                      <div className="section-title title-3">Last Updated</div>
                      <div className="body-2">{ formatDateTimeShort({ epochTimestamp: data.last_updated_timestamp }) }</div>
                    </section>
                  }
                  <section className="metadata-section">
                    <div className="section-title title-3">Frequent Users</div>
                    <FrequentUsers readers={ data.table_readers }/>
                  </section>
                </section>
                <section className="right-panel">
                  <EditableSection title="Tags">
                    <TagInput
                      resourceType={ ResourceType.table }
                      uriKey={ this.props.tableData.key }
                    />
                  </EditableSection>
                  <EditableSection title="Owners">
                    <OwnerEditor />
                  </EditableSection>
                </section>
              </section>
              {
                data.programmatic_descriptions.length > 0 &&
                <>
                  <div className="programmatic-title title-4">{PROGRMMATIC_DESC_HEADER}</div>
                  <hr className="programmatic-hr hr1"/>
                </>
              }
              {
                data.programmatic_descriptions
                  .map(d =>
                    <section key={d.source} className="column-layout-2">
                    <EditableSection title={d.source} readOnly={true}>
                      <EditableText
                        maxLength={999999}
                        value={d.text}
                        editable={false}
                        onSubmitValue={null}
                      />
                    </EditableSection>
                    </section>
                  )
              }
            </section>
            <section className="right-panel">
              { this.renderTabs() }
            </section>
          </article>
        </div>
      );
    }

    return (
      <DocumentTitle title={ `${ this.getDisplayName() } - Amundsen Table Details` }>
        { innerContent }
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    isLoading: state.tableMetadata.isLoading,
    statusCode: state.tableMetadata.statusCode,
    tableData: state.tableMetadata.tableData,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getTableData } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(TableDetail);
