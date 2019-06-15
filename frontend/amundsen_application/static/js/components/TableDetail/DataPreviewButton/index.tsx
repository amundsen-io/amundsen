import * as React from 'react';
import { connect } from 'react-redux';

import { Button, Modal, OverlayTrigger, Popover, Table } from 'react-bootstrap';
import Linkify from 'react-linkify'

import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'ducks/utilMethods';

import { PreviewData } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

enum LoadingStatus {
  ERROR = "error",
  FORBIDDEN = "forbidden",
  LOADING = "loading",
  SUCCESS = "success",
  UNAUTHORIZED = "unauthorized",
  UNAVAILABLE = "unavailable",
}

export interface StateFromProps {
  previewData: PreviewData;
  status: LoadingStatus;
}

export interface ComponentProps {
  modalTitle: string;
}

type DataPreviewButtonProps = StateFromProps & ComponentProps;

interface DataPreviewButtonState {
  status: LoadingStatus;
  showModal: boolean;
  previewData: PreviewData;
}

export function getStatusFromCode(httpErrorCode: number) {
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

export class DataPreviewButton extends React.Component<DataPreviewButtonProps, DataPreviewButtonState> {

  static getDerivedStateFromProps(nextProps, prevState) {
    const { previewData, status } = nextProps;
    return { ...prevState, previewData, status };
  }

  constructor(props) {
    super(props);

    this.state = {
      status: LoadingStatus.LOADING,
      showModal: false,
      previewData: {},
    }
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
    if (value === 0 || typeof value === "boolean") {
      return value.toString();
    }
    if (typeof value === "object") {
      return JSON.stringify(value);
    }

    return value || '';
  }

  renderModalBody() {
    const previewData = this.state.previewData;

    if (this.state.status === LoadingStatus.SUCCESS) {
      if (!previewData.columns || !previewData.data || previewData.columns.length === 0 || previewData.data.length === 0) {
        return (
          <div>
            No data available for preview
          </div>
        )
      }

      return (
        <div className='grid'>
          {
            previewData.columns.map((col, colId) => {
              const fieldName = col.column_name;
              return (
                <div key={fieldName} id={fieldName} className='grid-column'>
                  <div className='grid-cell grid-header subtitle-3'>
                    {fieldName.toUpperCase()}
                  </div>
                  {
                    previewData.data.map((row, rowId) => {
                      const cellId = `${colId}:${rowId}`;
                      const dataItemValue = this.getSanitizedValue(row[fieldName]);
                      return (
                        <div key={cellId} className='grid-cell'>
                          {dataItemValue}
                        </div>
                      );
                    })
                  }
                </div>
              )
            })
          }
        </div>
      )

    }

    if (this.state.status === LoadingStatus.UNAUTHORIZED) {
      return (
        <div>
          <Linkify>{previewData.error_text}</Linkify>
        </div>
      )
    }

    return null;
  }

  renderPreviewButton() {
    const previewData = this.state.previewData;

    // Based on the state, the preview button will show different things.
    let buttonText = 'Loading...';
    let disabled = true;
    let iconClass = 'icon-loading';
    let popoverText = 'The data preview is loading';

    // TODO: Setting hardcoded strings that should be customizable/translatable
    switch (this.state.status) {
      case LoadingStatus.SUCCESS:
      case LoadingStatus.UNAUTHORIZED:
        buttonText = 'Preview Data';
        iconClass = 'icon-preview';
        disabled = false;
        break;
      case LoadingStatus.FORBIDDEN:
        buttonText = 'Preview Forbidden';
        iconClass = 'icon-preview';
        popoverText = previewData.error_text || 'User is forbidden to preview this data';
        break;
      case LoadingStatus.UNAVAILABLE:
        buttonText = 'Preview Unavailable';
        iconClass = 'icon-preview';
        popoverText = 'This feature has not been configured by your service';
        break;
      case LoadingStatus.ERROR:
        buttonText = 'Preview Unavailable';
        iconClass = 'icon-preview';
        popoverText = previewData.error_text || 'An internal server error has occurred, please contact service admin';
        break;
      default:
        break;
    }

    const previewButton = (
      <button
        id="data-preview-button"
        className="btn btn-default btn-block"
        disabled={disabled}
        onClick={this.handleClick}
      >
         <img className={"icon icon-color " + iconClass} />
         <span>{buttonText}</span>
      </button>
    );

    if (!disabled) {
      return previewButton;
    }

    // when button is disabled, render button with Popover
    const popoverHover = (
      <Popover id="popover-trigger-hover">
        {popoverText}
      </Popover>
    );
    return (
      <OverlayTrigger
        trigger={['hover', 'focus']}
        placement='top'
        delayHide={200}
        overlay={popoverHover}>
          <div className="overlay-trigger">
            {previewButton}
          </div>
      </OverlayTrigger>
    )
  }

  render() {
    // else render button that triggers the preview data modal
    return (
      <div className="preview-data">
        {this.renderPreviewButton()}

        <Modal show={this.state.showModal} onHide={this.handleClose}>
          <Modal.Header className="text-center" closeButton={true}>
            <Modal.Title>
              {this.props.modalTitle}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {this.renderModalBody()}
          </Modal.Body>
        </Modal>
      </div>
    )
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    previewData: state.tableMetadata.preview.data,
    status: getStatusFromCode(state.tableMetadata.preview.status),
  };
};

export default connect<StateFromProps, {}, ComponentProps>(mapStateToProps, null)(DataPreviewButton);
