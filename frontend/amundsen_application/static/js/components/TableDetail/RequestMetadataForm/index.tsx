import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import './styles.scss';

import { NotificationType, RequestMetadataType, SendNotificationOptions, SendingState, TableMetadata } from 'interfaces';

import FlashMessage from 'components/common/FlashMessage'

import { GlobalState } from 'ducks/rootReducer';

import {
  TITLE_TEXT,
  FROM_LABEL,
  TO_LABEL,
  REQUEST_TYPE,
  TABLE_DESCRIPTION,
  COLUMN_DESCRIPTIONS,
  COLUMN_REQUESTED_COMMENT_PREFIX,
  COMMENT_PLACEHOLDER_COLUMN,
  COMMENT_PLACEHOLDER_DEFAULT,
  ADDITIONAL_DETAILS,
  RECIPIENT_LIST_DELIMETER,
  SEND_BUTTON,
  SEND_FAILURE_MESSAGE,
  SEND_INPROGRESS_MESSAGE,
  SEND_SUCCESS_MESSAGE,
} from './constants'
import { CloseRequestAction, OpenRequestAction, SubmitNotificationRequest } from 'ducks/notification/types';
import { closeRequestDescriptionDialog, submitNotification } from 'ducks/notification/reducer';

interface StateFromProps {
  columnName?: string;
  requestMetadataType?: RequestMetadataType;
  userEmail: string;
  tableMetadata: TableMetadata;
  tableOwners: string[];
  requestIsOpen: boolean;
  sendState: SendingState;
}

export interface DispatchFromProps {
  submitNotification: (
    recipients: string[],
    sender: string,
    notificationType: NotificationType,
    options?: SendNotificationOptions
  ) => SubmitNotificationRequest;
  closeRequestDescriptionDialog: () => CloseRequestAction;
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
    const recipients = recipientString.split(RECIPIENT_LIST_DELIMETER.trim())
    const sender = formData.get('sender') as string;
    const descriptionRequested = formData.get('table-description') === "on";
    const fieldsRequested = formData.get('column-description') === "on";
    const comment = formData.get('comment') as string;
    const { cluster, database, schema, name } = this.props.tableMetadata;
    this.props.submitNotification(
      recipients,
      sender,
      NotificationType.METADATA_REQUESTED,
      {
        comment,
        resource_name: `${schema}.${name}`,
        resource_path: `/table_detail/${cluster}/${database}/${schema}/${name}`,
        description_requested: descriptionRequested,
        fields_requested: fieldsRequested,
      }
    )
  };

  render() {
    const { columnName, requestIsOpen, requestMetadataType, sendState, tableMetadata, tableOwners, userEmail } = this.props;
    const tableDescriptionNeeded = requestMetadataType === RequestMetadataType.TABLE_DESCRIPTION;
    const colDescriptionNeeded = requestMetadataType === RequestMetadataType.COLUMN_DESCRIPTION;
    const defaultComment = columnName ? `${COLUMN_REQUESTED_COMMENT_PREFIX}${columnName}`: '';

    if (sendState !== SendingState.IDLE) {
      return (
        <div className="request-component">
          {this.renderFlashMessage()}
        </div>
      );
    }
    if (!requestIsOpen) {
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
            <input
              type="email"
              autoComplete="off"
              name="sender"
              className="form-control"
              required={true}
              value={userEmail}
              readOnly={true} />
          </div>
          <div id="recipients-form-group" className="form-group">
            <label>{TO_LABEL}</label>
            <input
              type="text"
              autoComplete="off"
              name="recipients"
              className="form-control"
              required={true}
              multiple={true}
              defaultValue={tableOwners.join(RECIPIENT_LIST_DELIMETER)}/>
          </div>
          <div id="request-type-form-group" className="form-group">
            <label>{REQUEST_TYPE}</label>
            <label className="select-label">
              <input
                type="checkbox"
                name="table-description"
                defaultChecked={tableDescriptionNeeded}
              />
              {TABLE_DESCRIPTION}
            </label>
            <label className="select-label">
              <input
                type="checkbox"
                name="column-description"
                defaultChecked={colDescriptionNeeded}
              />
              {COLUMN_DESCRIPTIONS}
            </label>
          </div>
          <div id="additional-comments-form-group" className="form-group">
            <label>{ADDITIONAL_DETAILS}</label>
            <textarea
              className="form-control"
              name="comment"
              placeholder={ colDescriptionNeeded ? COMMENT_PLACEHOLDER_COLUMN : COMMENT_PLACEHOLDER_DEFAULT }
              required={ colDescriptionNeeded }
              rows={ 8 }
              maxLength={ 2000 }
            >
              { defaultComment }
            </textarea>
          </div>
          <button id="submit-request-button" className="btn btn-primary submit-request-button" type="submit">
            <img className='icon icon-send'/>
            {SEND_BUTTON}
          </button>
        </form>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const userEmail = state.user.loggedInUser.email;
  const { columnName, requestMetadataType, requestIsOpen, sendState } = state.notification;
  const ownerObj = state.tableMetadata.tableOwners.owners;
  const mappedProps = {
    userEmail,
    requestIsOpen,
    sendState,
    tableMetadata: state.tableMetadata.tableData,
    tableOwners: Object.keys(ownerObj),
  };
  if (columnName) {
    mappedProps['columnName'] = columnName;
  }
  if (requestMetadataType) {
    mappedProps['requestMetadataType'] = requestMetadataType;
  }
  return mappedProps;
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ submitNotification, closeRequestDescriptionDialog } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(RequestMetadataForm);
