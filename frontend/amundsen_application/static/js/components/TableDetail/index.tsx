import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Link } from 'react-router-dom';

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

import { PreviewQueryParams, TableMetadata, User } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';
import BookmarkIcon from "components/common/Bookmark/BookmarkIcon";

export interface StateFromProps {
  isLoading: boolean;
  statusCode?: number;
  tableData: TableMetadata;
}

export interface DispatchFromProps {
  getTableData: (key: string, searchIndex?: string, source?: string, ) => GetTableDataRequest;
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
  private displayName: string;
  private key: string;
  private schema: string;
  private tableName: string;
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
      key: '',
      partition: { is_partitioned: false },
      schema: '',
      source: { source: '', source_type: '' },
      table_name: '',
      table_description: '',
      table_writer: { application_url: '', description: '', id: '', name: '' },
      table_readers: [],
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

    /*
    This 'key' is the `table_uri` format described in metadataservice. Because it contains the '/' character,
    we can't pass it as a single URL parameter without encodeURIComponent which makes ugly URLs.
    DO NOT CHANGE
    */
    this.key = params ? `${this.database}://${this.cluster}.${this.schema}/${this.tableName}` : '';

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

    this.props.getTableData(this.key, searchIndex, source);
    this.props.getPreviewData({ database: this.database, schema: this.schema, tableName: this.tableName });
  }

  getAvatarForUser(user: User, zIndex) {
    const popoverHoverFocus = (
      <Popover id="popover-trigger-hover-focus">
        { user.display_name }
      </Popover>
    );

    let link = user.profile_url;
    let target = '_blank';
    if (AppConfig.indexUsers.enabled) {
      link = `/user/${user.user_id}`;
      target = '';
    }

    return (
      <OverlayTrigger key={user.display_name} trigger={['hover', 'focus']} placement="top" overlay={popoverHoverFocus}>
        <Link
          to={ link }
          target={ target }
          className="avatar-overlap"
          id="frequent-users"
          onClick={logClick}
        >
          <Avatar name={user.display_name} size={25} round={true} style={{zIndex, position: 'relative'}} />
        </Link>
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

  renderAvatarForLineage = (href: string) => {
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

    // "Data Store" section
    const dataStoreRenderer = () => {
      return (
        <label className="m-auto">{ data.database.toUpperCase() }</label>
      );
    };
    entityCardSections.push({'title': 'Data Store', 'contentRenderer': dataStoreRenderer, 'isEditable': false});

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
        data.table_readers.map((entry, index) => {
          return this.getAvatarForUser(entry.reader, data.table_readers.length - index);
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
      const href = AppConfig.tableLineage.urlGenerator(this.database, this.cluster, this.schema, this.tableName);
      if (!!href) {
        entityCardSections.push({
          'title': 'Table Lineage' + (AppConfig.tableLineage.isBeta ? ' (beta)' : ''),
          'contentRenderer': () => { return this.renderAvatarForLineage(href) },
          'isEditable': false
        });
      };
    }

    // "Preview" Section
    const previewSectionRenderer = () => {
      const exploreSqlHref = AppConfig.tableProfile.isExploreEnabled ? this.getExploreSqlUrl() : '';
      return (
        <div>
          <DataPreviewButton modalTitle={ this.displayName } />
          {
            exploreSqlHref &&
              <a
                className="btn btn-default btn-block"
                href={exploreSqlHref}
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
          <Breadcrumb />
          <label className="d-block m-auto">Something went wrong...</label>
        </div>
      )
    } else {
        innerContent = (
          <div className="container table-detail">
            <Breadcrumb />
            <div className="row">
              <div className="detail-header col-xs-12 col-md-7 col-lg-8">
                <h1 className="detail-header-text">
                  { `${data.schema}.${data.table_name}` }
                  <BookmarkIcon bookmarkKey={ this.props.tableData.key } large={ true }/>
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
