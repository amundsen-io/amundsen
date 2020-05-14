import * as React from 'react';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { Issue } from 'interfaces';
import { getIssues } from 'ducks/issue/reducer';
import { logClick } from 'ducks/utilMethods';
import { GetIssuesRequest } from 'ducks/issue/types';
import LoadingSpinner from 'components/common/LoadingSpinner';
import ReportTableIssue from 'components/TableDetail/ReportTableIssue';
import { NO_DATA_ISSUES_TEXT } from './constants';
import './styles.scss';

export interface StateFromProps {
  issues: Issue[];
  total: number;
  allIssuesUrl: string;
  isLoading: boolean;
}

export interface DispatchFromProps {
  getIssues: (key: string) => GetIssuesRequest;
}

export interface ComponentProps {
  tableKey: string;
  tableName: string;
}

export type TableIssueProps = StateFromProps & DispatchFromProps & ComponentProps;

export class TableIssues extends React.Component<TableIssueProps> {
  componentDidMount() {
    this.props.getIssues(this.props.tableKey);
  }

  renderIssue = (issue: Issue, index: number) => {
    return (
      <div className="issue-banner" key={`issue-${index}`}>
        <span className={`table-issue-priority ${issue.priority_name}`}>
          {issue.priority_display_name}
        </span>
        <a id={`table-issue-link-${index}`} className="table-issue-link" target="_blank" href={issue.url} onClick={logClick}>
          <span>
            { issue.issue_key }
          </span>
        </a>
        <span className="issue-title-display-text truncated">
          <span className="issue-title-name">
            { issue.title }
          </span>
        </span>
        <span className="table-issue-status">
            {issue.status}
        </span>
      </div>
    );
  }

  renderMoreIssuesMessage = (count: number, url: string) => {
    return (
      <span className="table-more-issues" key="more-issue-link">
        <a id="more-issues-link" className="table-issue-more-issues" target="_blank" href={url} onClick={logClick}>
         View all {count} issues
        </a>
        |
        { this.renderReportIssueLink() }
      </span>
    );
  }

  renderReportIssueLink = () => {
    return (
      <div className="table-report-new-issue">
        <ReportTableIssue tableKey={ this.props.tableKey } tableName={ this.props.tableName }/>
      </div>
    );
  }

  renderIssueTitle = () => {
    return (
      <div className="section-title title-3">
        Issues
      </div>
    );
  }

  render() {
    if (this.props.isLoading) {
      return (
        <div>
          {this.renderIssueTitle()}
          <div className="table-issues">
            <LoadingSpinner />
          </div>
        </div>
      )
    }

    if (this.props.issues.length === 0) {
      return (
        <div>
          {this.renderIssueTitle()}
          <div className="table-issues">
            <div className="issue-banner">
              {NO_DATA_ISSUES_TEXT}
            </div>
          </div>
          { this.renderReportIssueLink()}
        </div>
      );
    }

    return (
      <div>
        {this.renderIssueTitle()}
        <div className="table-issues">
          { this.props.issues.map(this.renderIssue)}
        </div>
        { this.renderMoreIssuesMessage(this.props.total, this.props.allIssuesUrl)}
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    issues: state.issue.issues,
    total: state.issue.total,
    allIssuesUrl: state.issue.allIssuesUrl,
    isLoading: state.issue.isLoading,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getIssues }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(TableIssues);
