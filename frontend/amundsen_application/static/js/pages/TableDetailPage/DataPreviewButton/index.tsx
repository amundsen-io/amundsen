// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Modal, OverlayTrigger, Popover } from 'react-bootstrap';
import Linkify from 'react-linkify';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { getPreviewData } from 'ducks/tableMetadata/reducer';
import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'ducks/utilMethods';
import { PreviewData, PreviewQueryParams, TableMetadata } from 'interfaces';
import * as Constants from './constants';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

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
  getPreviewData: (queryParams: PreviewQueryParams) => void;
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
    const { tableData } = this.props;
    this.props.getPreviewData({
      database: tableData.database,
      schema: tableData.schema,
      tableName: tableData.name,
      cluster: tableData.cluster,
    });
  }

  handleClose = () => {
    this.setState({ showModal: false });
  };

  handleClick = (e) => {
    logClick(e);
    this.setState({ showModal: true });
  };

  getSanitizedValue(value) {
    // Display the string interpretation of the following "false-y" values
    // return 'Data Exceeds Render Limit' msg if column is too long
    let sanitizedValue = '';
    if (value === 0 || typeof value === 'boolean') {
      sanitizedValue = value.toString();
    } else if (typeof value === 'object') {
      sanitizedValue = JSON.stringify(value);
    } else {
      sanitizedValue = value;
    }

    if (sanitizedValue.length > Constants.PREVIEW_COLUMN_MAX_LEN) {
      return Constants.PREVIEW_COLUMN_MSG;
    }
    return sanitizedValue;
  }

  renderModalBody() {
    const { previewData } = this.props;

    if (this.props.status === LoadingStatus.SUCCESS) {
      if (
        !previewData.columns ||
        !previewData.data ||
        previewData.columns.length === 0 ||
        previewData.data.length === 0
      ) {
        return <div>No data available for preview</div>;
      }

      return (
        <div className="grid">
          {previewData.columns.map((col, colId) => {
            const fieldName = col.column_name;
            return (
              <div key={fieldName} id={fieldName} className="grid-column">
                <div className="grid-cell grid-header subtitle-3">
                  {fieldName.toUpperCase()}
                </div>
                {(previewData.data || []).map((row, rowId) => {
                  const cellId = `${colId}:${rowId}`;
                  const dataItemValue = this.getSanitizedValue(row[fieldName]);
                  return (
                    <div key={cellId} className="grid-cell">
                      {dataItemValue}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      );
    }

    if (this.props.status === LoadingStatus.UNAUTHORIZED) {
      return (
        <div>
          <Linkify>{previewData.error_text}</Linkify>
        </div>
      );
    }

    return null;
  }

  renderPreviewButton() {
    const { previewData } = this.props;

    // Based on the state, the preview button will show different things.
    let buttonText = 'Loading...';
    let disabled = true;
    let iconClass = 'icon-loading';
    let popoverText = 'The data preview is loading';

    // TODO: Setting hardcoded strings that should be customizable/translatable
    switch (this.props.status) {
      case LoadingStatus.SUCCESS:
      case LoadingStatus.UNAUTHORIZED:
        buttonText = 'Preview';
        iconClass = 'icon-preview';
        disabled = false;
        break;
      case LoadingStatus.FORBIDDEN:
        buttonText = 'Preview';
        iconClass = 'icon-preview';
        popoverText =
          previewData.error_text || 'User is forbidden to preview this data';
        break;
      case LoadingStatus.UNAVAILABLE:
        buttonText = 'Preview';
        iconClass = 'icon-preview';
        popoverText = 'This feature has not been configured by your service';
        break;
      case LoadingStatus.ERROR:
        buttonText = 'Preview';
        iconClass = 'icon-preview';
        popoverText =
          previewData.error_text ||
          'An internal server error has occurred, please contact service admin';
        break;
      default:
        break;
    }

    const previewButton = (
      <button
        id="data-preview-button"
        className="btn btn-default btn-lg"
        disabled={disabled}
        onClick={this.handleClick}
      >
        {buttonText}
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

  render() {
    return (
      <>
        {this.renderPreviewButton()}
        <Modal show={this.state.showModal} onHide={this.handleClose}>
          <Modal.Header className="text-center" closeButton>
            <Modal.Title>{this.props.modalTitle}</Modal.Title>
          </Modal.Header>
          <Modal.Body>{this.renderModalBody()}</Modal.Body>
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
