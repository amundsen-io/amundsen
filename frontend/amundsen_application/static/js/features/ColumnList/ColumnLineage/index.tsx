// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { emptyLineage } from 'ducks/tableMetadata/reducer';
import { getColumnLineageLink } from 'config/config-utils';
import { Lineage, LineageItem, TableMetadata } from 'interfaces/TableMetadata';
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
      &nbsp;
      <a href={link} className="body-link" rel="noreferrer" target="_blank">
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
}) => {
  const { downstream_entities, upstream_entities } = columnLineage;
  if (!downstream_entities.length && !upstream_entities.length) {
    return null;
  }
  const externalLink = getColumnLineageLink(tableData, columnName);
  return (
    <article className="column-lineage-wrapper">
      <LineageList
        link={externalLink}
        title={COLUMN_LINEAGE_UPSTREAM_TITLE}
        lineageItems={upstream_entities}
      />
      <LineageList
        link={externalLink}
        title={COLUMN_LINEAGE_DOWNSTREAM_TITLE}
        lineageItems={downstream_entities}
      />
    </article>
  );
};

export const mapStateToProps = (
  state: GlobalState,
  ownProps: ColumnLineageListOwnProps
) => {
  const { columnLineageMap, tableData } = state.tableMetadata;
  const columnLineage = columnLineageMap[ownProps.columnName] || emptyLineage;
  return {
    columnLineage,
    tableData,
  };
};

export default connect<StateFromProps, {}, ColumnLineageListOwnProps>(
  mapStateToProps
)(ColumnLineageList);
