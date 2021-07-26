// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Modal, OverlayTrigger, Popover } from 'react-bootstrap';
import Linkify from 'react-linkify';
import { connect } from 'react-redux';

import { getFreshnessData } from 'ducks/tableMetadata/reducer';
import { GlobalState } from 'ducks/rootReducer';
import { PreviewDataTable } from 'features/PreviewData';
import {
  PreviewData,
  TablePreviewQueryParams,
  TableMetadata,
} from 'interfaces';
import { logClick } from 'utils/analytics';

enum FetchingStatus {
  ERROR = 'error',
  LOADING = 'loading',
  SUCCESS = 'success',
  UNAVAILABLE = 'unavailable',
}

export interface StateFromProps {
  freshnessData: PreviewData;
  status: FetchingStatus;
  tableData: TableMetadata;
}

export interface DispatchFromProps {
  getFreshness: (queryParams: TablePreviewQueryParams) => void;
}

export interface ComponentProps {
  modalTitle: string;
}

type DataFreshnessButtonProps = StateFromProps &
  DispatchFromProps &
  ComponentProps;

interface DataFreshnessButtonState {
  showModal: boolean;
}

export function getStatusFromCode(httpErrorCode: number | null) {
  switch (httpErrorCode) {
    case null:
      return FetchingStatus.LOADING;
    case 200:
      // ok
      return FetchingStatus.SUCCESS;
    case 501:
      // No updated_at or inserted_at column
      return FetchingStatus.UNAVAILABLE;
    default:
      // default to generic error
      return FetchingStatus.ERROR;
  }
}

export class DataFreshnessButton extends React.Component<
  DataFreshnessButtonProps,
  DataFreshnessButtonState
> {
  constructor(props) {
    super(props);

    this.state = {
      showModal: false,
    };
  }

  componentDidMount() {
    const { tableData, getFreshness } = this.props;

    getFreshness({
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

  renderModalBody() {
    const { freshnessData, status } = this.props;

    if (status === FetchingStatus.SUCCESS) {
      return <PreviewDataTable isLoading={false} previewData={freshnessData} />;
    }

    if (status === FetchingStatus.ERROR) {
      return (
        <div>
          <Linkify>{freshnessData.error_text}</Linkify>
        </div>
      );
    }

    return null;
  }

  renderFreshnessButton() {
    const { freshnessData, status } = this.props;

    // Based on the state, the preview button will show different things.
    let buttonText = 'Fetching...';
    let disabled = true;
    let popoverText = 'The data freshness is being fetched';

    switch (status) {
      case FetchingStatus.SUCCESS:
        buttonText = 'Freshness';
        disabled = false;
        break;
      case FetchingStatus.UNAVAILABLE:
        buttonText = 'Freshness';
        popoverText = 'This feature has not been configured by your service';
        break;
      case FetchingStatus.ERROR:
        buttonText = 'Freshness';
        popoverText =
          freshnessData.error_text ||
          'An internal server error has occurred, please contact service admin';
        break;
      default:
        break;
    }

    const freshnessButton = (
      <button
        id="data-freshness-button"
        className="btn btn-default btn-lg"
        disabled={disabled}
        type="button"
        onClick={this.handleClick}
      >
        {buttonText}
      </button>
    );

    if (!disabled) {
      return freshnessButton;
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
        <div className="overlay-trigger">{freshnessButton}</div>
      </OverlayTrigger>
    );
  }

  render() {
    const { modalTitle } = this.props;
    const { showModal } = this.state;
    return (
      <>
        {this.renderFreshnessButton()}
        <Modal show={showModal} onHide={this.handleClose}>
          <Modal.Header className="text-center" closeButton>
            <Modal.Title>{modalTitle}</Modal.Title>
          </Modal.Header>
          <Modal.Body>{this.renderModalBody()}</Modal.Body>
        </Modal>
      </>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  freshnessData: state.tableMetadata.freshness.data,
  status: getStatusFromCode(state.tableMetadata.freshness.status),
  tableData: state.tableMetadata.tableData,
});

export const mapDispatchToProps = (dispatch: any) => ({
  getFreshness: (queryParams: TablePreviewQueryParams) => {
    dispatch(getFreshnessData(queryParams));
  },
});

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(DataFreshnessButton);
