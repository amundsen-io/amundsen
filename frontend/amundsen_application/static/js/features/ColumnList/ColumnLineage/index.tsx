// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { emptyLineage } from 'ducks/tableMetadata/reducer';
import { getColumnLineageLink } from 'config/config-utils';
import { Lineage, LineageItem, TableMetadata } from 'interfaces/TableMetadata';
import { logClick } from 'utils/analytics';
import ColumnLineageLoader from '../ColumnLineageLoader';
import {
  COLUMN_LINEAGE_LIST_SIZE,
  COLUMN_LINEAGE_DOWNSTREAM_TITLE,
  COLUMN_LINEAGE_UPSTREAM_TITLE,
  COLUMN_LINEAGE_MORE_TEXT,
} from '../constants';

import './styles.scss';

interface ColumnLineageListOwnProps {
  columnName: string;
  tableKey: string;
}

interface StateFromProps {
  columnLineage: Lineage;
  tableData: TableMetadata;
  isLoading: boolean;
}

type ColumnLineageListProps = ColumnLineageListOwnProps & StateFromProps;

interface LineageListProps {
  link: string;
  title: string;
  lineageItems: LineageItem[];
}

const getLink = (table) => {
  const { cluster, database, schema, name } = table;
  return `/table_detail/${cluster}/${database}/${schema}/${name}?source=column_lineage`;
};

const handleLineageClick = (e) => {
  logClick(e, {
    target_id: 'column_lineage',
  });
};

const handleSeeMoreClick = (e) => {
  logClick(e, {
    target_id: 'column_lineage_see_more',
  });
};

const renderLineageLinks = (entity, index) => {
  if (index >= COLUMN_LINEAGE_LIST_SIZE) {
    return null;
  }
  return (
    <div>
      <a
        href={getLink(entity)}
        className="body-link"
        target="_blank"
        rel="noreferrer"
        onClick={handleLineageClick}
      >
        {entity.schema}.{entity.name}
      </a>
    </div>
  );
};

const LineageList: React.FC<LineageListProps> = ({
  link,
  title,
  lineageItems,
}) => (
  <div className="column-lineage-list">
    <div className="header-row">
      <span className="column-lineage-title">{title}</span>
      <a
        href={link}
        className="body-link"
        rel="noreferrer"
        target="_blank"
        onClick={handleSeeMoreClick}
      >
        {COLUMN_LINEAGE_MORE_TEXT}
      </a>
    </div>
    {lineageItems.map(renderLineageLinks)}
  </div>
);

export const ColumnLineageList: React.FC<ColumnLineageListProps> = ({
  columnName,
  columnLineage,
  tableData,
  isLoading,
}) => {
  if (isLoading) {
    return <ColumnLineageLoader />;
  }
  const { downstream_entities, upstream_entities } = columnLineage;
  const externalLink = getColumnLineageLink(tableData, columnName);
  if (!downstream_entities.length && !upstream_entities.length) {
    return null;
  }
  return (
    <article className="column-lineage-wrapper">
      {upstream_entities.length && (
        <LineageList
          link={externalLink}
          title={COLUMN_LINEAGE_UPSTREAM_TITLE}
          lineageItems={upstream_entities}
        />
      )}
      {downstream_entities.length && (
        <LineageList
          link={externalLink}
          title={COLUMN_LINEAGE_DOWNSTREAM_TITLE}
          lineageItems={downstream_entities}
        />
      )}
    </article>
  );
};

export const mapStateToProps = (
  state: GlobalState,
  ownProps: ColumnLineageListOwnProps
) => {
  const { columnLineageMap, tableData } = state.tableMetadata;
  const columnStateObject = columnLineageMap[ownProps.columnName];
  const lineage =
    (columnStateObject && columnStateObject.lineage) || emptyLineage;
  const isLoading = columnStateObject && columnStateObject.isLoading;
  return {
    tableData,
    isLoading,
    columnLineage: lineage,
  };
};

export default connect<StateFromProps, {}, ColumnLineageListOwnProps>(
  mapStateToProps
)(ColumnLineageList);
