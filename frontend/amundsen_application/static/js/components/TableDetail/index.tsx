import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import * as Avatar from 'react-avatar';
import * as DocumentTitle from 'react-document-title';
import * as qs from 'simple-query-string';

import { GlobalState } from 'ducks/rootReducer';
import { getPreviewData, getTableData } from 'ducks/tableMetadata/reducer';
import { GetTableDataRequest } from 'ducks/tableMetadata/types';

import AppConfig from 'config/config';
import AvatarLabel from 'components/common/AvatarLabel';
import Breadcrumb from 'components/common/Breadcrumb';
import EntityCard from 'components/common/EntityCard';
import Flag from "components/common/Flag";
import LoadingSpinner from 'components/common/LoadingSpinner';
import ScrollTracker from "components/common/ScrollTracker";
import TagInput from 'components/Tags/TagInput';

import DataPreviewButton from './DataPreviewButton';
import DetailList from './DetailList';
import OwnerEditor from './OwnerEditor';
import TableDescEditableText from './TableDescEditableText';
import WatermarkLabel from "./WatermarkLabel";
import { logClick } from 'ducks/utilMethods';

import { OverlayTrigger, Popover } from 'react-bootstrap';
import { RouteComponentProps } from 'react-router';

import { PreviewQueryParams, TableMetadata } from './types';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface StateFromProps {
  isLoading: boolean;
  statusCode?: number;
  tableData: TableMetadata;
}

export interface DispatchFromProps {
  getTableData: (cluster: string, database: string, schema: string, tableName: string, searchIndex?: string, source?: string, ) => GetTableDataRequest;
  getPreviewData: (queryParams: PreviewQueryParams) => void;
}

type TableDetailProps = StateFromProps & DispatchFromProps;

interface TableDetailState {
  isLoading: boolean;
  statusCode: number;
  tableData: TableMetadata;
}

export class TableDetail extends React.Component<TableDetailProps & RouteComponentProps<any>, TableDetailState> {
  private cluster: string;
  private database: string;
  private schema: string;
  private tableName: string;
  private displayName: string;
  public static defaultProps: TableDetailProps = {
    getTableData: () => undefined,
    getPreviewData: () => undefined,
    isLoading: true,
    statusCode: null,
    tableData: {
      cluster: '',
      columns: [],
      database: '',
      is_editable: false,
      is_view: false,
      schema: '',
      table_name: '',
      table_description: '',
      table_writer: { application_url: '', description: '', id: '', name: '' },
      partition: { is_partitioned: false },
      table_readers: [],
      source: { source: '', source_type: '' },
      watermarks: [],
    },
  };

  static getDerivedStateFromProps(nextProps, prevState) {
    const { isLoading, statusCode, tableData } = nextProps;
    return { isLoading, statusCode, tableData };
  }

  constructor(props) {
    super(props);

    const { match } = props;
    const params = match.params;
    this.cluster = params ? params.cluster : '';
    this.database = params ? params.db : '';
    this.schema = params ? params.schema : '';
    this.tableName = params ? params.table : '';
    this.displayName = params ? `${this.schema}.${this.tableName}` : '';

    this.state = {
      isLoading: props.isLoading,
      statusCode: props.statusCode,
      tableData: props.tableData,
    }
  }

  componentDidMount() {
    const params = qs.parse(this.props.location.search);
    const searchIndex = params['index'];
    const source = params['source'];

    /* update the url stored in the browser history to remove params used for logging purposes */
    if (searchIndex !== undefined) {
      window.history.replaceState({}, '', `${window.location.origin}${window.location.pathname}`);
    }

    this.props.getTableData(this.cluster, this.database, this.schema, this.tableName, searchIndex, source);
    this.props.getPreviewData({ database: this.database, schema: this.schema, tableName: this.tableName });
  }

  frequentUserOnClick = (e) => {
    logClick(e, {
      target_id: 'frequent-users',
    })
  };

  getAvatarForUser(fullName, profileUrl) {
    const popoverHoverFocus = (
      <Popover id="popover-trigger-hover-focus">
        {fullName}
      </Popover>);

    if (profileUrl.length !== 0) {
      return (
        <OverlayTrigger key={fullName} trigger={['hover', 'focus']} placement="top" overlay={popoverHoverFocus}>
          <a href={profileUrl} target='_blank'
             style={{ display: 'inline-block', marginLeft: '-5px', backgroundColor: 'white', borderRadius: '90%'}}
             onClick={this.frequentUserOnClick}
          >
            <Avatar name={fullName} size={25} round={true} style={{ border: '1px solid white' }} />
          </a>
        </OverlayTrigger>
      );
    }
    return (
      <OverlayTrigger key={fullName} trigger={['hover', 'focus']} placement="top" overlay={popoverHoverFocus}>
        <div style={{display: 'inline-block', marginLeft: '-5px',
          backgroundColor: 'white', borderRadius: '90%'}}>
          <Avatar name={fullName} size={25} round={true} style={{border: '1px solid white'}}/>
        </div>
      </OverlayTrigger>
    );
  }

  getAvatarForTableWriter(tableWriter) {
    const appName = tableWriter.id;
    const appUrl = tableWriter.application_url;
    const appType = tableWriter.name;
    const sourceImage = (appType === 'Airflow') ?  '/static/images/airflow.jpeg' : '';
    const avatarLabel = <AvatarLabel label={appName} src={sourceImage}/>;

    if (appUrl.length !== 0) {
      return (
        <a href={appUrl} target='_blank' id="explore-writer" onClick={logClick}>
          { avatarLabel }
        </a>
      );
    }

    return avatarLabel;
  }

  getAvatarForTableSource = (source) => {
    if (source !== null) {
      const image = (source.source_type === 'github')? '/static/images/github.png': '';
      const avatarLabel = <AvatarLabel label={this.displayName} src={image}/>;

      return (
        <a href={ source.source }
           target='_blank'
           id="explore-source"
           onClick={ logClick }
        >
          { avatarLabel }
        </a>
      );
    }
  };

  getAvatarForLineage = () => {
    const href = AppConfig.tableLineage.urlGenerator(this.database, this.cluster, this.schema, this.tableName);
    return (
      <a href={ href } target='_blank' id="explore-lineage" onClick={logClick}>
        <AvatarLabel label={ this.displayName } src={ AppConfig.tableLineage.iconPath }/>
      </a>
    );
  };

  getExploreSqlUrl = () => {
    const partition = this.state.tableData.partition;
    if (partition.is_partitioned) {
      return AppConfig.tableProfile.exploreUrlGenerator(this.database, this.cluster, this.schema, this.tableName, partition.key, partition.value);
    }
    return AppConfig.tableProfile.exploreUrlGenerator(this.database, this.cluster, this.schema, this.tableName);
  };

  createEntityCardSections = () => {
    const data = this.state.tableData;

    const entityCardSections = [];

    // "Owned By" section
    const ownerSectionRenderer = () => {
      return (
        <OwnerEditor
          readOnly={false}
        />
      );
    };
    entityCardSections.push({'title': 'Owned By', 'contentRenderer': ownerSectionRenderer, 'isEditable': false});


    // "Frequent Users" section
    const readerSectionRenderer = () => {
      return (data.table_readers && data.table_readers.length > 0) ?
        data.table_readers.map((entry) => {
          const fullName = entry.reader.display_name;
          const profileUrl = entry.reader.profile_url;

          return (
              this.getAvatarForUser(fullName, profileUrl)
          );
        }) :
        (<label className="m-auto">No frequent users exist</label>);
    };
    entityCardSections.push({
        'title': 'Frequent Users',
        'infoText': 'Top 5 frequent users of this table',
        'contentRenderer': readerSectionRenderer,
        'isEditable': false
    });


    // "Generated By" section
    const writer = data.table_writer;
    if (writer && writer.application_url !== null) {
      const appSectionRenderer = () => {
        return this.getAvatarForTableWriter(writer)
      };

      entityCardSections.push({'title': 'Generated By', 'contentRenderer': appSectionRenderer, 'isEditable': false});
    }

    // "source"
    const source = data.source;
    if (source && source.source !== null) {
      const sourceRenderer = () => {
        return this.getAvatarForTableSource(source);
      };

      entityCardSections.push({'title': 'Source Code', 'contentRenderer': sourceRenderer, 'isEditable': false});
    }

    // "Lineage" Section
    if (AppConfig.tableLineage.isEnabled) {
      entityCardSections.push({
        'title': 'Table Lineage' + (AppConfig.tableLineage.isBeta ? ' (beta)' : ''),
        'contentRenderer': this.getAvatarForLineage,
        'isEditable': false
      });
    }

    // "Preview" Section
    const previewSectionRenderer = () => {
      return (
        <div>
          <DataPreviewButton modalTitle={ this.displayName } />
          {
            AppConfig.tableProfile.isExploreEnabled &&
              <a
                className="btn btn-default btn-block"
                href={this.getExploreSqlUrl()}
                role="button"
                target="_blank"
                id="explore-sql"
                onClick={logClick}
              >
                <img className="icon icon-color icon-database"/>
                Explore with SQL
              </a>
          }
        </div>
      );
    };
    entityCardSections.push({
      'title': 'Table Profile' + (AppConfig.tableProfile.isBeta ? ' (beta)' : ''),
      'contentRenderer': previewSectionRenderer,
      'isEditable': false
    });

    // "Tags" Section
    const sectionContentRenderer = (readOnly: boolean) => {
      return (
        <TagInput
          readOnly={readOnly}
        />
      );
    };
    entityCardSections.push({'title': 'Tags', 'contentRenderer': sectionContentRenderer, 'isEditable': true});


    return entityCardSections;
  };

  render() {
    const data = this.state.tableData;
    let innerContent;
    if (this.state.isLoading) {
      innerContent = <LoadingSpinner/>;
    } else if (this.state.statusCode === 404){
      this.props.history.push('/404');
    } else if (this.state.statusCode === 500) {
      innerContent = (
        <div className="container error-label">
          <Breadcrumb path='/' text='Search Results'/>
          <label className="d-block m-auto">Something went wrong...</label>
        </div>
      )
    } else {
        innerContent = (
          <div className="container table-detail">
            <Breadcrumb path='/' text='Search Results'/>
            <div className="row">
              <div className="detail-header col-xs-12 col-md-7 col-lg-8">
                <h1 className="detail-header-text">
                  { `${data.schema}.${data.table_name}` }
                </h1>
                {
                  data.is_view && <Flag text="Table View" labelStyle="primary" />
                }
                {
                  !data.is_view && <WatermarkLabel watermarks={ data.watermarks }/>
                }
                <TableDescEditableText
                  maxLength={ 750 }
                  value={ data.table_description }
                  editable={ data.is_editable }
                />
              </div>
              <div className="col-xs-12 col-md-5 float-md-right col-lg-4">
                <EntityCard sections={ this.createEntityCardSections() }/>
              </div>
              <div className="col-xs-12 col-md-7 col-lg-8">
                <div className="detail-list-header title-1">Columns</div>
                <DetailList
                  columns={ data.columns }
                />
              </div>
            </div>
            <ScrollTracker targetId={ this.displayName }/>
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
  return bindActionCreators({ getPreviewData, getTableData } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(TableDetail);
