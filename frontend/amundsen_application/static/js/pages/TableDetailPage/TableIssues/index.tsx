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
import { NO_DATA_ISSUES_TEXT } from './constants';
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
      <span className="section-title title-3 create-issue-error">
        Could not create issue!
      </span>
    ) : (
      ''
    );

    return (
      <div className="table-issues-header">
        <span className="section-title title-3">Issues</span>
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
      allIssuesUrl,
      openIssuesUrl,
      closedIssuesUrl,
      total,
      openCount,
    } = this.props;
    const totalCount = total ? total : 0;
    const openIssueCount = openCount ? openCount : 0;
    const closedIssueCount = totalCount - openIssueCount;
    const hasIssues = issues.length !== 0 || totalCount > 0;

    const reportIssueLink = (
      <div className={`table-report-new-issue ${hasIssues ? 'ml-1' : ''}`}>
        <ReportTableIssue tableKey={tableKey} tableName={tableName} />
      </div>
    );

    if (!hasIssues) {
      return reportIssueLink;
    }
    if (openIssuesUrl && closedIssuesUrl) {
      return (
        <span className="table-more-issues" key="more-issue-link">
          <a
            id="open-issues-link"
            className="table-issue-more-issues"
            target="_blank"
            rel="noreferrer"
            href={openIssuesUrl}
            onClick={logClick}
          >
            View {openIssueCount} open issues
          </a>
          |
          <a
            id="closed-issues-link"
            className="table-issue-more-issues ml-1"
            target="_blank"
            rel="noreferrer"
            href={closedIssuesUrl}
            onClick={logClick}
          >
            View {closedIssueCount} closed issues
          </a>
          |{reportIssueLink}
        </span>
      );
    } else {
      return (
        <span className="table-more-issues" key="more-issue-link">
          <a
            id="more-issues-link"
            className="table-issue-more-issues"
            target="_blank"
            rel="noreferrer"
            href={allIssuesUrl}
            onClick={logClick}
          >
            View all {total} issues
          </a>
          |{reportIssueLink}
        </span>
      );
    }
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
