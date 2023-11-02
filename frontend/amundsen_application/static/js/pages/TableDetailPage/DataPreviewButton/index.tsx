// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Modal, OverlayTrigger, Popover, Button } from 'react-bootstrap';
import Linkify from 'react-linkify';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { faker } from '@faker-js/faker';
import Papa from 'papaparse';

import { getPreviewData } from 'ducks/tableMetadata/reducer';
import { GlobalState } from 'ducks/rootReducer';
import { PreviewDataTable } from 'features/PreviewData';
import {
  PreviewData,
  PreviewColumnItem,
  TablePreviewQueryParams,
  TableMetadata,
} from 'interfaces';
import { logClick } from 'utils/analytics';
import AvatarLabel from 'components/AvatarLabel';
import LoadingSpinner from 'components/LoadingSpinner';
import {
  previewExportEnabled
} from 'config/config-utils';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

const BUTTON_IMAGE = '/static/images/preview.png';

// Create a new instance of Faker
// const faker = new Faker({ locale: 'en' });


enum LoadingStatus {
  ERROR = 'error',
  FORBIDDEN = 'forbidden',
  LOADING = 'loading',
  SUCCESS = 'success',
  UNAUTHORIZED = 'unauthorized',
  UNAVAILABLE = 'unavailable',
}

export interface StateFromProps {
  previewData: PreviewData;
  status: LoadingStatus;
  tableData: TableMetadata;
}

export interface DispatchFromProps {
  getPreviewData: (queryParams: TablePreviewQueryParams) => void;
}

export interface ComponentProps {
  modalTitle: string;
}

type DataPreviewButtonProps = StateFromProps &
  DispatchFromProps &
  ComponentProps;

interface DataPreviewButtonState {
  showModal: boolean;
}

type Column = {
  column_name: string;
  column_type: string;
};

type RowData = {
  [key: string]: any; // Use 'any' or a more specific type if possible
};

export function getStatusFromCode(httpErrorCode: number | null) {
  switch (httpErrorCode) {
    case null:
      return LoadingStatus.LOADING;
    case 200:
      // ok
      return LoadingStatus.SUCCESS;
    case 401:
      // user is unauthorized to see content
      return LoadingStatus.UNAUTHORIZED;
    case 403:
      // user is authorized, but forbidden from resource
      return LoadingStatus.FORBIDDEN;
    case 501:
      // preview client was not configured
      return LoadingStatus.UNAVAILABLE;
    default:
      // default to generic error
      return LoadingStatus.ERROR;
  }
}

export class DataPreviewButton extends React.Component<
  DataPreviewButtonProps,
  DataPreviewButtonState
> {
  constructor(props) {
    super(props);

    this.state = {
      showModal: false,
    };
  }

  componentDidMount() {
    // const { tableData, getPreviewData } = this.props;

    // getPreviewData({
    //   database: tableData.database,
    //   schema: tableData.schema,
    //   tableName: tableData.name,
    //   cluster: tableData.cluster,
    // });
  }

  handleClose = () => {
    this.setState({ showModal: false });
  };

  handleClick = (e) => {
    const { tableData, getPreviewData, previewData } = this.props;

    logClick(e);

    getPreviewData({
      database: tableData.database,
      schema: tableData.schema,
      tableName: tableData.name,
      cluster: tableData.cluster,
    });

    this.setState({ showModal: true });
  };

  renderModalBody() {
    const { previewData, status } = this.props;

    if (status === LoadingStatus.LOADING) {
      return <LoadingSpinner />;
    }

    if (status === LoadingStatus.SUCCESS) {
      return <PreviewDataTable isLoading={false} previewData={previewData} />;
    }

    if (status === LoadingStatus.UNAUTHORIZED) {
      return (
        <div>
          <Linkify>{previewData.error_text}</Linkify>
        </div>
      );
    }

    return null;
  }

  renderPreviewButton() {
    const { previewData, status } = this.props;

    // Based on the state, the preview button will show different things.
    let buttonText = 'Loading...';
    let disabled = true;
    let popoverText = 'The data preview is loading';

    // TODO: Setting hardcoded strings that should be customizable/translatable
    // switch (status) {
    //   case LoadingStatus.SUCCESS:
    //   case LoadingStatus.UNAUTHORIZED:
    //     buttonText = 'Preview';
    //     disabled = false;
    //     break;
    //   case LoadingStatus.FORBIDDEN:
    //     buttonText = 'Preview';
    //     popoverText =
    //       previewData.error_text || 'User is forbidden to preview this data';
    //     break;
    //   case LoadingStatus.UNAVAILABLE:
    //     buttonText = 'Preview';
    //     popoverText = 'This feature has not been configured by your service';
    //     break;
    //   case LoadingStatus.ERROR:
    //     buttonText = 'Preview';
    //     popoverText =
    //       previewData.error_text ||
    //       'An internal server error has occurred, please contact service admin';
    //     break;
    //   default:
    //     break;
    // }
    buttonText = 'Preview';
    disabled = false;

    const previewButton = (
      <button
        id="data-preview-button"
        className="btn btn-default btn-lg"
        disabled={disabled}
        onClick={this.handleClick}
      >
        <AvatarLabel
          label={buttonText}
          src={BUTTON_IMAGE}
          round={true}
        />
      </button>
    );

    if (!disabled) {
      return previewButton;
    }

    // when button is disabled, render button with Popover
    const popoverHover = (
      <Popover id="popover-trigger-hover">{popoverText}</Popover>
    );

    return (
      <OverlayTrigger
        trigger={['hover', 'focus']}
        placement="top"
        delayHide={200}
        overlay={popoverHover}
      >
        {/* Disabled buttons don't trigger hover/focus events so we need a wrapper */}
        <div className="overlay-trigger">{previewButton}</div>
      </OverlayTrigger>
    );
  }

  handleExportPreview = () => {
    const { modalTitle, previewData } = this.props;

    // Convert JSON to CSV using PapaParse
    if (previewData && previewData.data && previewData.columns) {
      const quoteColumns = previewData.columns.map(column =>
        (column.column_type.toLowerCase().includes('string') ||
        column.column_type.toLowerCase().includes('varchar') ||
        column.column_type.toLowerCase().includes('variant') ||
        column.column_type.toLowerCase().includes('json')));

      const csv = Papa.unparse(previewData.data, {
        quotes: quoteColumns, // Only quote string fields
        delimiter: ",", // Use a comma as the delimiter
      });
      this.triggerDownload(csv, `preview.${modalTitle}.csv`);
    }
  };

  triggerDownload = (csv, filename) => {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  handleExportScrubbed = () => {
    const { modalTitle, previewData } = this.props;
    const fakeData = this.generateFakeData(previewData.columns, 100);
    const csv = Papa.unparse(fakeData);
    this.triggerDownload(csv, `scrubbed.${modalTitle}.csv`);
  };

  generateFakeValueByType = (column: PreviewColumnItem): any => {
    // Check for specific patterns in column names to infer data type
    if (/email/i.test(column.column_name)) {
      return faker.internet.email();
    } else if (/name/i.test(column.column_name)) {
      return faker.person.fullName();
    } else if (/address/i.test(column.column_name)) {
      return faker.location.streetAddress();
    } else if (/date/i.test(column.column_name)) {
      return faker.date.past().toISOString();
    }

    // Fallback to column types
    const col_type = column.column_type.toLowerCase();
    if (col_type == 'string' ||
        col_type.includes('varchar')) {
      return faker.random.word();
    }
    else if (col_type.includes('number') ||
             col_type.includes('int')) {
      return faker.number.int();
    }
    else if (col_type.includes('decimal') ||
             col_type.includes('int')) {
      return faker.number.float();
    }
    else if (col_type.includes('bool')) {
      return faker.datatype.boolean();
    }
    else if (col_type.includes('date')) {
      return faker.date.past().toISOString();
    }
    else if (col_type.includes('variant') ||
             col_type.includes('json')) {
      return faker.datatype.json();
    }
    else {
        console.log(`DataPreviewButton: Found unhandled column data type '${column.column_type.toLowerCase()}'`)
        return faker.lorem.word();
    }
  };

  generateFakeData = (columns: PreviewColumnItem[] | undefined, rowCount: number): Record<string, any>[] => {
    const fakeData: Record<string, any>[] = [];

    if (columns) {
      for (let i = 0; i < rowCount; i++) {
        let rowData: Record<string, any> = {};
        columns.forEach(column => {
          rowData[column.column_name] = this.generateFakeValueByType(column);
        });
        fakeData.push(rowData);
      }
    }

    return fakeData;
  };

  render() {
    const { modalTitle, status } = this.props;
    const { showModal } = this.state;

    return (
      <>
        {this.renderPreviewButton()}
        <Modal
          className="data-preview-modal"
          show={showModal}
          onHide={this.handleClose}
        >
          <Modal.Header className="text-center" closeButton>
            <Modal.Title>{modalTitle}</Modal.Title>
          </Modal.Header>
          <Modal.Body style={{ overflowY: 'auto', maxHeight: '400px' }}>{this.renderModalBody()}</Modal.Body>
          {(previewExportEnabled() && status === LoadingStatus.SUCCESS) && (
            <Modal.Footer>
              <Button variant="primary" onClick={this.handleExportPreview}>
                Export Preview
              </Button>
              <Button variant="primary" onClick={this.handleExportScrubbed}>
                Export Scrubbed
              </Button>
            </Modal.Footer>
          )}
        </Modal>
      </>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  previewData: state.tableMetadata.preview.data,
  status: getStatusFromCode(state.tableMetadata.preview.status),
  tableData: state.tableMetadata.tableData,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getPreviewData }, dispatch);

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(DataPreviewButton);
