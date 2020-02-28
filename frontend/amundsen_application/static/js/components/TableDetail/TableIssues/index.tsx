import * as React from 'react';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { Issue } from 'interfaces'; 
import { getIssues } from 'ducks/issue/reducer'; 
import { logClick } from 'ducks/utilMethods';
import { GetIssuesRequest } from 'ducks/issue/types';
import './styles.scss';
import { issueTrackingEnabled } from 'config/config-utils';
import { SEE_ADDITIONAL_ISSUES_TEXT } from './constants';


export interface StateFromProps {
  issues: Issue[]; 
  remainingIssues: number; 
  remainingIssuesUrl: string; 
}

export interface DispatchFromProps {
  getIssues: (key: string) => GetIssuesRequest; 
}

export interface ComponentProps {
  tableKey: string;
}

export type TableIssueProps = StateFromProps & DispatchFromProps & ComponentProps; 

export class TableIssues extends React.Component<TableIssueProps> {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    if (issueTrackingEnabled()) {
      this.props.getIssues(this.props.tableKey);
    }
  }

  renderIssue = (issue: Issue, index: number) => {
    return (
      <div className="issue-banner" key={`issue-${index}`}>
        <a id={`table-issue-link-${index}`} className="table-issue-link" target="_blank" href={issue.url} onClick={logClick}>
          <img className="icon icon-red-triangle-warning "/>
          { issue.issue_key }
        </a>
        <span className="issue-title-display-text">
          <span className="issue-title-name">
           "{ issue.title }
          </span>"
        </span>
      </div>
    ); 
  }

  renderMoreIssuesMessage = (count: number, url: string) => {
    if (count === 0) {
      return ''; 
     }

    return (
      <div className="issue-banner" key="more-issue-link">
        <img className="icon icon-red-triangle-warning "/>
        <a id="more-issues-link" className="table-issue-more-issues" target="_blank" href={url} onClick={logClick}>
          { SEE_ADDITIONAL_ISSUES_TEXT }
        </a> 
    </div>
    );
  }

  render() {
    if (!issueTrackingEnabled()) {
      return ''; 
    }
    
    if (this.props.issues.length === 0) {
      return null;
    }

    return (
      <div className="table-issues">
        { this.props.issues.map(this.renderIssue)}
        { this.renderMoreIssuesMessage(this.props.remainingIssues, this.props.remainingIssuesUrl)}
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    issues: state.issue.issues, 
    remainingIssues: state.issue.remainingIssues, 
    remainingIssuesUrl: state.issue.remainingIssuesUrl
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getIssues }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(TableIssues);
