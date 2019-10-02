import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import './styles.scss';

import { NotificationType, SendNotificationOptions, SendingState } from 'interfaces';

import FlashMessage from 'components/common/FlashMessage'

import { GlobalState } from 'ducks/rootReducer';

import {
  TITLE_TEXT,
  FROM_LABEL,
  TO_LABEL,
  REQUEST_TYPE,
  TABLE_DESCRIPTION,
  COLUMN_DESCRIPTIONS,
  ADDITIONAL_DETAILS,
  SEND_BUTTON,
  SEND_FAILURE_MESSAGE,
  SEND_INPROGRESS_MESSAGE,
  SEND_SUCCESS_MESSAGE,
} from './constants'
import { ToggleRequestAction, SubmitNotificationRequest } from 'ducks/notification/types';
import { closeRequestDescriptionDialog, submitNotification } from 'ducks/notification/reducer';

interface StateFromProps {
  userEmail: string;
  displayName: string;
  tableOwners: Array<string>;
  requestIsOpen: boolean;
  sendState: SendingState;
}

export interface DispatchFromProps {
  submitNotification: (
    recipients: Array<string>,
    sender: string,
    notificationType: NotificationType,
    options?: SendNotificationOptions
  ) => SubmitNotificationRequest;
  closeRequestDescriptionDialog: () => ToggleRequestAction;
}

export type RequestMetadataProps = StateFromProps & DispatchFromProps;

interface RequestMetadataState {}

export class RequestMetadataForm extends React.Component<RequestMetadataProps, RequestMetadataState> {
  public static defaultProps: Partial<RequestMetadataProps> = {};

  constructor(props) {
    super(props);
  }

  componentWillUnmount = () => {
    this.props.closeRequestDescriptionDialog();
  }

  closeDialog = () => {
    this.props.closeRequestDescriptionDialog();
  }

  getFlashMessageString = (): string => {
    switch(this.props.sendState) {
      case SendingState.COMPLETE:
        return SEND_SUCCESS_MESSAGE;
      case SendingState.ERROR:
        return SEND_FAILURE_MESSAGE;
      case SendingState.WAITING:
        return SEND_INPROGRESS_MESSAGE;
      default:
        return '';
    }
  };

  renderFlashMessage = () => {
    return (
      <FlashMessage
        iconClass='icon-mail'
        message={this.getFlashMessageString()}
        onClose={this.closeDialog}
      />
    )
  }

  submitNotification = (event) => {
    event.preventDefault();
    const form = document.getElementById("RequestForm") as HTMLFormElement;
    const formData = new FormData(form);
    const recipientString = formData.get('recipients') as string
    const recipients = recipientString.split(",")
    const sender = formData.get('sender') as string;
    const descriptionRequested = formData.get('table-description') === "on";
    const fieldsRequested = formData.get('column-description') === "on";
    const comment = formData.get('comment') as string;
    this.props.submitNotification(
      recipients,
      sender,
      NotificationType.METADATA_REQUESTED,
      {
        comment,
        resource_name: this.props.displayName,
        resource_url: window.location.href,
        description_requested: descriptionRequested,
        fields_requested: fieldsRequested,
      }
    )
  };

  render() {
    if (this.props.sendState !== SendingState.IDLE) {
      return (
        <div className="request-component">
          {this.renderFlashMessage()}
        </div>
      );
    }
    if (!this.props.requestIsOpen) {
      return (null);
    }
    return (
      <div className="request-component expanded">
        <div id="request-metadata-title" className="form-group request-header">
          <h3 className="title">{TITLE_TEXT}</h3>
          <button type="button" className="btn btn-close" aria-label={"Close"} onClick={this.closeDialog}/>
        </div>
        <form onSubmit={ this.submitNotification } id="RequestForm">
          <div id="sender-form-group" className="form-group">
            <label>{FROM_LABEL}</label>
            <input type="email" name="sender" className="form-control" required={true} value={this.props.userEmail} readOnly={true}/>
          </div>
          <div id="recipients-form-group" className="form-group">
            <label>{TO_LABEL}</label>
            <input type="email" name="recipients" className="form-control" required={true} multiple={true} defaultValue={this.props.tableOwners.join(",")}/>
          </div>
          <div id="request-type-form-group" className="form-group">
            <label>{REQUEST_TYPE}</label>
            <label className="select-label"><input type="checkbox" name="table-description"/>{TABLE_DESCRIPTION}</label>
            <label className="select-label"><input type="checkbox" name="column-description"/>{COLUMN_DESCRIPTIONS}</label>
          </div>
          <div id="additional-comments-form-group" className="form-group">
            <label>{ADDITIONAL_DETAILS}</label>
            <textarea className="form-control" name="comment" rows={ 8 } maxLength={ 2000 } />
          </div>
          <button id="submit-request-button" className="btn btn-primary" type="submit">
            {SEND_BUTTON}
          </button>
        </form>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const userEmail = state.user.loggedInUser.email;
  const displayName = `${state.tableMetadata.tableData.schema}.${state.tableMetadata.tableData.table_name}`;
  const ownerObj = state.tableMetadata.tableOwners.owners;
  const { requestIsOpen, sendState } = state.notification;
  return {
    userEmail,
    displayName,
    requestIsOpen,
    sendState,
    tableOwners: Object.keys(ownerObj),
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ submitNotification, closeRequestDescriptionDialog } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(RequestMetadataForm);
