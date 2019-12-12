import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { RouteComponentProps } from 'react-router';
import * as qs from 'simple-query-string';

import { GlobalState } from 'ducks/rootReducer';
import { getTableData } from 'ducks/tableMetadata/reducer';
import { GetTableDataRequest } from 'ducks/tableMetadata/types';

import AppConfig from 'config/config';
import BadgeList from 'components/common/BadgeList';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import Breadcrumb from 'components/common/Breadcrumb';
import DataPreviewButton from 'components/TableDetail/DataPreviewButton';
import ColumnList from 'components/TableDetail/ColumnList';
import ExploreButton from 'components/TableDetail/ExploreButton';
import Flag from 'components/common/Flag';
import FrequentUsers from 'components/TableDetail/FrequentUsers';
import LoadingSpinner from 'components/common/LoadingSpinner';
import LineageLink from 'components/TableDetail/LineageLink';
import OwnerEditor from 'components/TableDetail/OwnerEditor';
import SourceLink from 'components/TableDetail/SourceLink';
import TableDescEditableText from 'components/TableDetail/TableDescEditableText';
import WatermarkLabel from 'components/TableDetail/WatermarkLabel';
import WriterLink from 'components/TableDetail/WriterLink';
import TagInput from 'components/Tags/TagInput';
import { TableMetadata } from 'interfaces/TableMetadata';

import { EditableSection } from 'components/TableDetail/EditableSection';
import { getDatabaseDisplayName, getDatabaseIconClass, notificationsEnabled } from 'config/config-utils';

import './styles';
import RequestDescriptionText from './RequestDescriptionText';
import RequestMetadataForm from './RequestMetadataForm';

export interface StateFromProps {
  isLoading: boolean;
  statusCode?: number;
  tableData: TableMetadata;
}

export interface DispatchFromProps {
  getTableData: (key: string, searchIndex?: string, source?: string, ) => GetTableDataRequest;
}

type TableDetailProps = StateFromProps & DispatchFromProps;

class TableDetail extends React.Component<TableDetailProps & RouteComponentProps<any>> {
  private cluster: string;
  private database: string;
  private displayName: string;
  private key: string;
  private schema: string;
  private tableName: string;
  private didComponentMount: boolean = false;

  constructor(props) {
    super(props);

    const { match } = props;
    const params = match.params;
    this.cluster = params ? params.cluster : '';
    this.database = params ? params.db : '';
    this.schema = params ? params.schema : '';
    this.tableName = params ? params.table : '';
    this.displayName = params ? `${this.schema}.${this.tableName}` : '';

    /*
    This 'key' is the `table_uri` format described in metadataservice. Because it contains the '/' character,
    we can't pass it as a single URL parameter without encodeURIComponent which makes ugly URLs.
    DO NOT CHANGE
    */
    this.key = params ? `${this.database}://${this.cluster}.${this.schema}/${this.tableName}` : '';

  }

  componentDidMount() {
    // TODO - Move into utility function
    const params = qs.parse(this.props.location.search);
    const searchIndex = params['index'];
    const source = params['source'];
    /* update the url stored in the browser history to remove params used for logging purposes */
    if (searchIndex !== undefined || source !== undefined) {
      window.history.replaceState({}, '', `${window.location.origin}${window.location.pathname}`);
    }

    this.props.getTableData(this.key, searchIndex, source);
    this.didComponentMount = true;
  }

  render() {
    let innerContent;
    // We want to avoid rendering the previous table's metadata before new data is fetched in componentDidMount
    if (this.props.isLoading || !this.didComponentMount) {
      innerContent = <LoadingSpinner/>;
    } else if (this.props.statusCode === 500) {
      innerContent = (
        <div className="container error-label">
          <Breadcrumb />
          <label className="d-block m-auto">Something went wrong...</label>
        </div>
      );
    } else {
      const data = this.props.tableData;
      innerContent = (
        <div className="resource-detail-layout table-detail-2">
          {
            notificationsEnabled() && <RequestMetadataForm />
          }
          <header className="resource-header">
            <div className="header-section">
              {/* TODO - add Breadcrumb here */}
              <img className={"icon icon-header " + getDatabaseIconClass(data.database)} />
            </div>
            <div className="header-section header-title">
              <h3 className="header-title-text truncated">
                  { this.displayName }
              </h3>
              <BookmarkIcon bookmarkKey={ this.props.tableData.key }/>
              <div className="body-2">
                Datasets &bull;&nbsp;
                { getDatabaseDisplayName(data.database) }
                &nbsp;&bull;&nbsp;
                { data.cluster }
                &nbsp;
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
              <DataPreviewButton modalTitle={ this.displayName }/>
              <ExploreButton tableData={ data }/>
            </div>
          </header>
          <main className="column-layout-1">
            <section className="left-panel">
              {/*
                TODO - Add a banner here if necessary
                <section className="banner">optional banner</section>
              */}
              <EditableSection title="Description">
                <TableDescEditableText
                  maxLength={ AppConfig.editableText.tableDescLength }
                  value={ data.table_description }
                  editable={ data.is_editable }
                />
              </EditableSection>
              { !data.table_description && notificationsEnabled() && <RequestDescriptionText/> }
              <section className="column-layout-2">
                <section className="left-panel">
                  {
                    !data.is_view &&
                    <>
                      <div className="section-title title-3">Date Range</div>
                      <WatermarkLabel watermarks={ data.watermarks }/>
                    </>
                  }
                  <div className="section-title title-3">Frequent Users</div>
                  <FrequentUsers readers={ data.table_readers }/>
                </section>
                <section className="right-panel">
                  <EditableSection title="Tags">
                    <TagInput/>
                  </EditableSection>

                  <EditableSection title="Owners">
                    <OwnerEditor readOnly={false}/>
                  </EditableSection>

                </section>
              </section>
            </section>
            <section className="right-panel">
              <ColumnList columns={ data.columns }/>
            </section>
          </main>
        </div>
      );
    }

    return (
      <DocumentTitle title={ `${this.displayName} - Amundsen Table Details` }>
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
