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
  DashboardMetadata,
  CreateIssuePayload,
  NotificationPayload,
  NotificationType,
} from 'interfaces';
import {
  getIssueDescriptionTemplate,
  issueTrackingProjectSelectionEnabled,
  getProjectSelectionTitle,
  getProjectSelectionHint,
} from 'config/config-utils';
import * as Constants from './constants';

import './styles.scss';

export interface ComponentProps {
  dashboardKey: string;
  dashboardName: string;
}

export interface DispatchFromProps {
  createIssue: (
    createIssuePayload: CreateIssuePayload,
    notificationPayload: NotificationPayload
  ) => CreateIssueRequest;
}

export interface StateFromProps {
  dashboardOwners: string[];
  userEmail: string;
  dashboardMetadata: DashboardMetadata;
}

interface ReportDashboardIssueState {
  isOpen: boolean;
  issuePriority: string;
}

export type ReportDashboardIssueProps = StateFromProps &
  DispatchFromProps &
  ComponentProps;

export class ReportDashboardIssue extends React.Component<
  ReportDashboardIssueProps,
  ReportDashboardIssueState
> {
  constructor(props) {
    super(props);

    this.state = { isOpen: false, issuePriority: Constants.PRIORITY.P2 };
  }

  submitForm = (event) => {
    logClick(event);
    event.preventDefault();
    const form = document.getElementById(
      'report-dashboard-issue-form'
    ) as HTMLFormElement;
    const formData = new FormData(form);

    const { createIssue: createIssueInterface } = this.props;
    const createIssuePayload = this.getCreateIssuePayload(formData);
    const notificationPayload = this.getNotificationPayload();

    createIssueInterface(createIssuePayload, notificationPayload);
    this.setState({ isOpen: false });
  };

  getCreateIssuePayload = (formData: FormData): CreateIssuePayload => {
    const {
      dashboardKey,
      dashboardMetadata: { cluster, product, group_name, name },
      dashboardOwners
    } = this.props;
    const { issuePriority } = this.state;
    const title = formData.get('title') as string;
    const description = formData.get('description') as string;
    const projectKey = issueTrackingProjectSelectionEnabled()
      ? (formData.get('project_key') as string)
      : '';
    const resourcePath = `/dashboard/${encodeURIComponent(dashboardKey)}`;

    return {
      title,
      description,
      owner_ids: dashboardOwners,
      frequent_user_ids: [],
      priority_level: issuePriority,
      project_key: projectKey,
      key: dashboardKey,
      resource_path: resourcePath,
    };
  };

  getNotificationPayload = (): NotificationPayload => {
    const {
      dashboardKey,
      dashboardMetadata: { cluster, product, group_name, name },
      dashboardOwners,
      userEmail,
    } = this.props;
    const owners = dashboardOwners;
    const resourceName = `${group_name}.${name}`;
    const resourcePath = `/dashboard/${encodeURIComponent(dashboardKey)}`;

    return {
      recipients: owners,
      sender: userEmail,
      notificationType: NotificationType.DATA_ISSUE_REPORTED,
      options: {
        resource_name: resourceName,
        resource_path: resourcePath,
      },
    };
  };

  toggle = (event) => {
    const { isOpen } = this.state;

    logClick(event);
    this.setState({ isOpen: !isOpen });
  };

  handlePriorityChange = (event) => {
    this.setState({ issuePriority: event });
  };

  renderProjectSelectionTitle = () =>
    issueTrackingProjectSelectionEnabled() ? (
      <label htmlFor="project">{getProjectSelectionTitle()}</label>
    ) : (
      ''
    );

  renderProjectSelectionField = () =>
    issueTrackingProjectSelectionEnabled() ? (
      <input
        name="project_key"
        className="form-control"
        maxLength={200}
        placeholder={getProjectSelectionHint()}
        aria-label="Issue tracking project key"
      />
    ) : (
      ''
    );

  render() {
    const { isOpen, issuePriority } = this.state;

    return (
      <>
        {/* eslint-disable jsx-a11y/anchor-is-valid */}
        <a
          href="javascript:void(0)"
          className="body-link"
          style={{ fontFamily: 'IBM Plex Mono', fontSize: '14px'}}
          data-type="report-issues-link"
          onClick={this.toggle}
        >
          {Constants.REPORT_DATA_ISSUE_TEXT}
        </a>
        {isOpen && (
          <div className="report-dashboard-issue-modal">
            <h3 className="data-issue-header">
              {Constants.REPORT_DATA_ISSUE_TEXT}
            </h3>
            <button
              type="button"
              className="btn btn-close"
              data-type="report-issues-close"
              onClick={this.toggle}
            >
              <span className="sr-only">{Constants.CLOSE}</span>
            </button>
            <form id="report-dashboard-issue-form" onSubmit={this.submitForm}>
              <div className="form-group">
                <label>{Constants.TITLE_LABEL}</label>
                <input
                  name="title"
                  className="form-control"
                  required
                  maxLength={200}
                />
              </div>
              <div className="form-group">
                <label>{Constants.DESCRIPTION_LABEL}</label>
                <textarea
                  name="description"
                  className="form-control"
                  rows={5}
                  required
                  maxLength={2000}
                  defaultValue={getIssueDescriptionTemplate()}
                  aria-label="Issue description"
                />
              </div>
              <label htmlFor="priority">{Constants.PRIORITY_LABEL}</label>
              <div className="form-group">
                <ToggleButtonGroup
                  type="radio"
                  name="priority"
                  id="priority"
                  value={issuePriority}
                  onChange={this.handlePriorityChange}
                >
                  <ToggleButton value={Constants.PRIORITY.P3}>
                    {Constants.PRIORITY.P3}
                  </ToggleButton>
                  <ToggleButton value={Constants.PRIORITY.P2}>
                    {Constants.PRIORITY.P2}
                  </ToggleButton>
                  <ToggleButton value={Constants.PRIORITY.P1}>
                    {Constants.PRIORITY.P1}
                  </ToggleButton>
                  <ToggleButton value={Constants.PRIORITY.P0}>
                    {Constants.PRIORITY.P0}
                  </ToggleButton>
                </ToggleButtonGroup>
              </div>
              {this.renderProjectSelectionTitle()}
              <div className="submit-row">
                {this.renderProjectSelectionField()}
                <button className="btn btn-primary submit" type="submit">
                  {Constants.SUBMIT_BUTTON_LABEL}
                </button>
              </div>
            </form>
            <div className="data-owner-notification">
              {Constants.DASHBOARD_OWNERS_NOTE}
            </div>
          </div>
        )}
      </>
    );
  }
}
export const mapStateToProps = (state: GlobalState) => {
  const { dashboard, user } = state;
  const ownerObj = dashboard.dashboard.owners;
  const dashboardOwnersEmails = Object.keys(ownerObj);
  const userEmail = user.loggedInUser.email;

  return {
    userEmail,
    dashboardOwners: dashboardOwnersEmails,
    dashboardMetadata: dashboard.dashboard,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ createIssue }, dispatch);

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(ReportDashboardIssue);
