// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { Issue } from 'interfaces';
import { getIssues } from 'ducks/issue/reducer';
import { GetIssuesRequest } from 'ducks/issue/types';
import { logClick } from 'utils/analytics';
import ReportTableIssue from '../ReportTableIssue';
import {
  ISSUES_TITLE,
  NO_DATA_ISSUES_TEXT,
  CREATE_ISSUE_ERROR_TEXT,
} from './constants';
import './styles.scss';

export interface StateFromProps {
  issues: Issue[];
  total?: number;
  openCount?: number;
  allIssuesUrl?: string;
  openIssuesUrl?: string;
  closedIssuesUrl?: string;
  isLoading: boolean;
  createIssueFailure: boolean;
}

export interface DispatchFromProps {
  getIssues: (key: string) => GetIssuesRequest;
}

export interface ComponentProps {
  tableKey: string;
  tableName: string;
}

export type TableIssueProps = StateFromProps &
  DispatchFromProps &
  ComponentProps;

const ShimmeringIssuesLoader: React.FC = () => (
  <div className="shimmer-issues">
    <div className="shimmer-issues-row shimmer-issues-line--1 is-shimmer-animated" />
    <div className="shimmer-issues-row shimmer-issues-line--2 is-shimmer-animated" />
  </div>
);

export class TableIssues extends React.Component<TableIssueProps> {
  componentDidMount() {
    const { getIssues: getIssuesInterface, tableKey } = this.props;

    getIssuesInterface(tableKey);
  }

  renderIssue = (issue: Issue, index: number) => (
    <div className="issue-banner" key={`issue-${index}`}>
      <span className={`table-issue-priority ${issue.priority_name}`}>
        {issue.priority_display_name}
      </span>
      <a
        id={`table-issue-link-${index}`}
        className="table-issue-link"
        target="_blank"
        href={issue.url}
        onClick={logClick}
        rel="noreferrer"
      >
        <span>{issue.issue_key}</span>
      </a>
      <span className="issue-title-display-text truncated">
        <span className="issue-title-name">{issue.title}</span>
      </span>
      <span className="table-issue-status">{issue.status}</span>
    </div>
  );

  renderIssueTitle = () => {
    const { createIssueFailure } = this.props;

    const createIssueErrorMsg = createIssueFailure ? (
      <span className="section-title create-issue-error">
        {CREATE_ISSUE_ERROR_TEXT}
      </span>
    ) : (
      ''
    );

    return (
      <div className="table-issues-header">
        <span className="section-title">{ISSUES_TITLE}</span>
        {createIssueErrorMsg}
      </div>
    );
  };

  renderIssueContent = () => {
    const { issues } = this.props;

    if (issues.length === 0) {
      return <div className="issue-banner">{NO_DATA_ISSUES_TEXT}</div>;
    }
    return issues.map(this.renderIssue);
  };

  renderIssueFooter = () => {
    const {
      issues,
      tableKey,
      tableName,
      openIssuesUrl,
      closedIssuesUrl,
      total,
      openCount,
    } = this.props;
    const totalCount = total || 0;
    const openIssueCount = openCount || 0;
    const closedIssueCount = totalCount - openIssueCount;

    const hasIssues = issues.length !== 0 || totalCount > 0;

    const reportIssueLink = (
      <div className={`table-report-new-issue ${hasIssues ? 'last-item' : ''}`}>
        <ReportTableIssue tableKey={tableKey} tableName={tableName} />
      </div>
    );

    if (!hasIssues) {
      return reportIssueLink;
    }

    return (
      <span className="table-more-issues" key="more-issue-link">
        {openIssuesUrl && (
          <a
            id="open-issues-link"
            className="table-issue-more-issues"
            target="_blank"
            rel="noreferrer"
            href={openIssuesUrl}
            onClick={logClick}
          >
            {openIssueCount} open
          </a>
        )}
        {openIssuesUrl && closedIssuesUrl ? '|' : ''}
        {closedIssuesUrl && (
          <a
            id="closed-issues-link"
            className={`table-issue-more-issues ${
              openIssuesUrl ? 'last-item' : ''
            }`}
            target="_blank"
            rel="noreferrer"
            href={closedIssuesUrl}
            onClick={logClick}
          >
            {closedIssueCount} closed
          </a>
        )}
        |{reportIssueLink}
      </span>
    );
  };

  render() {
    const { isLoading } = this.props;

    if (isLoading) {
      return (
        <>
          {this.renderIssueTitle()}
          <div className="table-issues">
            <ShimmeringIssuesLoader />
          </div>
        </>
      );
    }

    return (
      <>
        {this.renderIssueTitle()}
        <div className="table-issues">{this.renderIssueContent()}</div>
        {this.renderIssueFooter()}
      </>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  issues: state.issue.issues,
  total: state.issue.total,
  openCount: state.issue.openCount,
  allIssuesUrl: state.issue.allIssuesUrl,
  openIssuesUrl: state.issue.openIssuesUrl,
  closedIssuesUrl: state.issue.closedIssuesUrl,
  isLoading: state.issue.isLoading,
  createIssueFailure: state.issue.createIssueFailure,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getIssues }, dispatch);

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(TableIssues);
