// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { ToggleButton, ToggleButtonGroup } from 'react-bootstrap';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { GlobalState } from 'ducks/rootReducer';

import { createIssue } from 'ducks/issue/reducer';
import { CreateIssueRequest } from 'ducks/issue/types';
import { logClick } from 'utils/analytics';
import {
  TableMetadata,
  CreateIssuePayload,
  NotificationPayload,
  NotificationType,
} from 'interfaces';
import { getIssueDescriptionTemplate } from 'config/config-utils';
import * as Constants from './constants';

import './styles.scss';

export interface ComponentProps {
  tableKey: string;
  tableName: string;
}

export interface DispatchFromProps {
  createIssue: (
    createIssuePayload: CreateIssuePayload,
    notificationPayload: NotificationPayload
  ) => CreateIssueRequest;
}

export interface StateFromProps {
  tableOwners: string[];
  userEmail: string;
  tableMetadata: TableMetadata;
}

interface ReportTableIssueState {
  isOpen: boolean;
  issuePriority: string;
}

export type ReportTableIssueProps = StateFromProps &
  DispatchFromProps &
  ComponentProps;

export class ReportTableIssue extends React.Component<
  ReportTableIssueProps,
  ReportTableIssueState
> {
  constructor(props) {
    super(props);

    this.state = { isOpen: false, issuePriority: Constants.PRIORITY.LOW };
  }

  submitForm = (event) => {
    logClick(event);
    event.preventDefault();
    const form = document.getElementById(
      'report-table-issue-form'
    ) as HTMLFormElement;
    const formData = new FormData(form);

    const createIssuePayload = this.getCreateIssuePayload(formData);
    const notificationPayload = this.getNotificationPayload();
    this.props.createIssue(createIssuePayload, notificationPayload);
    this.setState({ isOpen: false });
  };

  getCreateIssuePayload = (formData: FormData): CreateIssuePayload => {
    const {
      tableKey,
      tableMetadata: { cluster, database, schema, name },
    } = this.props;
    const { issuePriority } = this.state;
    const title = formData.get('title') as string;
    const description = formData.get('description') as string;
    const priorityLevel = issuePriority;
    const resourcePath = `/table_detail/${cluster}/${database}/${schema}/${name}`;

    return {
      title,
      description,
      priority_level: priorityLevel,
      key: tableKey,
      resource_path: resourcePath,
    };
  };

  getNotificationPayload = (): NotificationPayload => {
    const {
      tableMetadata: { cluster, database, schema, name },
    } = this.props;
    const owners = this.props.tableOwners;
    const resourceName = `${schema}.${name}`;
    const resourcePath = `/table_detail/${cluster}/${database}/${schema}/${name}`;

    return {
      recipients: owners,
      sender: this.props.userEmail,
      notificationType: NotificationType.DATA_ISSUE_REPORTED,
      options: {
        resource_name: resourceName,
        resource_path: resourcePath,
      },
    };
  };

  toggle = (event) => {
    if (!this.state.isOpen) {
      logClick(event);
    }
    this.setState({ isOpen: !this.state.isOpen });
  };

  onPriorityChange = (event) => {
    this.setState({ issuePriority: event });
  };

  render() {
    const { isOpen, issuePriority } = this.state;

    return (
      <>
        {/* eslint-disable jsx-a11y/anchor-is-valid */}
        <a
          href="javascript:void(0)"
          className="body-link"
          onClick={this.toggle}
        >
          {Constants.REPORT_DATA_ISSUE_TEXT}
        </a>
        {isOpen && (
          <div className="report-table-issue-modal">
            <h3 className="data-issue-header">
              {Constants.REPORT_DATA_ISSUE_TEXT}
            </h3>
            <button
              type="button"
              className="btn btn-close"
              onClick={this.toggle}
            >
              <span className="sr-only">{Constants.CLOSE}</span>
            </button>
            <form id="report-table-issue-form" onSubmit={this.submitForm}>
              <div className="form-group">
                <label>Title</label>
                <input
                  name="title"
                  className="form-control"
                  required
                  maxLength={200}
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  className="form-control"
                  rows={5}
                  required
                  maxLength={2000}
                >
                  {getIssueDescriptionTemplate()}
                </textarea>
              </div>
              <label htmlFor="priority">Priority</label>
              <div>
                <ToggleButtonGroup
                  type="radio"
                  name="priority"
                  id="priority"
                  className="priority-btn-group"
                  value={issuePriority}
                  onChange={this.onPriorityChange}
                >
                  <ToggleButton value={Constants.PRIORITY.LOW}>
                    Low
                  </ToggleButton>
                  <ToggleButton value={Constants.PRIORITY.MEDIUM}>
                    Medium
                  </ToggleButton>
                  <ToggleButton value={Constants.PRIORITY.HIGH}>
                    High
                  </ToggleButton>
                </ToggleButtonGroup>
                <button
                  className="btn btn-primary issue-submit-btn submit"
                  type="submit"
                >
                  Submit
                </button>
              </div>
            </form>
            <div className="data-owner-notification">
              {Constants.TABLE_OWNERS_NOTE}
            </div>
          </div>
        )}
      </>
    );
  }
}
export const mapStateToProps = (state: GlobalState) => {
  const ownerObj = state.tableMetadata.tableOwners.owners;
  const tableOwnersEmails = Object.keys(ownerObj);
  const userEmail = state.user.loggedInUser.email;
  return {
    userEmail,
    tableOwners: tableOwnersEmails,
    tableMetadata: state.tableMetadata.tableData,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ createIssue }, dispatch);

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(ReportTableIssue);
