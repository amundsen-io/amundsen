// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { GetTableQualityChecksRequest } from 'ducks/tableMetadata/types';
import { getTableQualityChecks } from 'ducks/tableMetadata/reducer';
import { TableQualityChecks } from 'interfaces/TableMetadata';
import { formatDateTimeShort } from 'utils/dateUtils';
import * as Constants from './constants';

import './styles.scss';

export interface StateFromProps {
  status: number | null;
  checks: TableQualityChecks;
  isLoading: boolean;
}

export interface DispatchFromProps {
  getTableQualityChecksDispatch: (key: string) => GetTableQualityChecksRequest;
}

export interface ComponentProps {
  tableKey: string;
}

export type TableQualityChecksProps = StateFromProps &
  DispatchFromProps &
  ComponentProps;

const ShimmeringIssuesLoader: React.FC = () => (
  <div className="shimmer-issues">
    <div className="shimmer-issues-row shimmer-issues-line--1 is-shimmer-animated" />
    <div className="shimmer-issues-row shimmer-issues-line--2 is-shimmer-animated" />
  </div>
);

export class TableQualityChecksLabel extends React.Component<TableQualityChecksProps> {
  componentDidMount() {
    const { getTableQualityChecksDispatch, tableKey } = this.props;
    getTableQualityChecksDispatch(tableKey);
  }

  render() {
    const { isLoading, checks } = this.props;
    if (isLoading) {
      return <ShimmeringIssuesLoader />;
    }
    let checkText;
    if (checks.num_checks_failed > 0) {
      checkText = `${checks.num_checks_failed} out of ${checks.num_checks_total} checks failed`;
    } else {
      checkText = `All ${checks.num_checks_total} checks failed`;
    }
    return (
      <section className="metadata-section table-quality-checks">
        <div className="section-title">{Constants.COMPONENT_TITLE}</div>
        <div className="checks-status">{checkText}</div>
        <div className="last-run-timestamp">
          Latest run at:
          <time>
            {formatDateTimeShort({
              timestamp: checks.last_run_timestamp,
            })}
          </time>
        </div>
        <a
          href={checks.external_url}
          className="body-link"
          target="_blank"
          rel="noreferrer"
        >
          {Constants.SEE_MORE_LABEL}
        </a>
      </section>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  status: state.tableMetadata.tableQualityChecks.status,
  isLoading: state.tableMetadata.tableQualityChecks.isLoading,
  checks: state.tableMetadata.tableQualityChecks.checks,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    { getTableQualityChecksDispatch: getTableQualityChecks },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(TableQualityChecksLabel);
