// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';
import { OverlayTrigger, Popover } from 'react-bootstrap';

import { GlobalState } from 'ducks/rootReducer';
import { initialLineageState } from 'ducks/lineage/reducer';
import { TAB_URL_PARAM } from 'components/TabsComponent/constants';
import { getColumnLineageLink } from 'config/config-utils';
import { TableMetadata } from 'interfaces/TableMetadata';
import { Lineage, LineageItem } from 'interfaces/Lineage';
import { TABLE_TAB } from 'pages/TableDetailPage/constants';
import { logClick } from 'utils/analytics';

import ColumnLineageLoader from '../ColumnLineageLoader';
import {
  COLUMN_LINEAGE_LIST_SIZE,
  COLUMN_LINEAGE_DOWNSTREAM_TITLE,
  COLUMN_LINEAGE_UPSTREAM_TITLE,
  COLUMN_LINEAGE_MORE_TEXT,
  DELAY_SHOW_POPOVER_MS,
} from '../constants';

import './styles.scss';

interface ColumnLineageListOwnProps {
  columnName: string;
  singleColumnDisplay?: boolean;
}

interface StateFromProps {
  columnLineage: Lineage;
  tableData: TableMetadata;
  isLoading: boolean;
}

type ColumnLineageListProps = ColumnLineageListOwnProps & StateFromProps;

interface LineageListProps {
  direction: string;
  lineageItems: LineageItem[];
  link: string;
  title: string;
}

const getLink = (table, direction) => {
  const { cluster, database, schema, name } = table;
  // TODO - column lineage should return the column name as a separate field
  const [tableName, columnName] = name.split('/');
  return (
    `/table_detail/${cluster}/${database}/${schema}/${tableName}` +
    `?source=column_lineage_${direction}&${TAB_URL_PARAM}=${TABLE_TAB.COLUMN}&column=${columnName}`
  );
};

const renderLineageLinks = (entity, index, direction) => {
  if (index >= COLUMN_LINEAGE_LIST_SIZE) {
    return null;
  }
  const lineageDisplayText = entity.schema + '.' + entity.name;
  return (
    <OverlayTrigger
      key={lineageDisplayText}
      trigger={['hover', 'focus']}
      placement="top"
      delayShow={DELAY_SHOW_POPOVER_MS}
      overlay={
        <Popover id="popover-trigger-hover-focus">{lineageDisplayText}</Popover>
      }
    >
      <div className="column-lineage-item">
        <a
          href={getLink(entity, direction)}
          className="body-link"
          target="_blank"
          rel="noreferrer"
          onClick={(e) =>
            logClick(e, { target_id: `column_lineage`, value: direction })
          }
        >
          {lineageDisplayText}
        </a>
      </div>
    </OverlayTrigger>
  );
};

const LineageList: React.FC<LineageListProps> = ({
  link,
  direction,
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
        onClick={(e) =>
          logClick(e, {
            target_id: `column_lineage_see_more`,
            value: direction,
          })
        }
      >
        {COLUMN_LINEAGE_MORE_TEXT}
      </a>
    </div>
    {lineageItems.map((item, index) =>
      renderLineageLinks(item, index, direction)
    )}
  </div>
);

export const ColumnLineageList: React.FC<ColumnLineageListProps> = ({
  columnName,
  singleColumnDisplay,
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
    <article
      className={`column-lineage-wrapper ${
        singleColumnDisplay && 'single-column-display'
      }`}
    >
      {upstream_entities.length !== 0 && (
        <LineageList
          direction="upstream"
          lineageItems={upstream_entities}
          link={externalLink}
          title={COLUMN_LINEAGE_UPSTREAM_TITLE}
        />
      )}
      {downstream_entities.length !== 0 && (
        <LineageList
          direction="downstream"
          lineageItems={downstream_entities}
          link={externalLink}
          title={COLUMN_LINEAGE_DOWNSTREAM_TITLE}
        />
      )}
    </article>
  );
};

export const mapStateToProps = (
  state: GlobalState,
  ownProps: ColumnLineageListOwnProps
) => {
  const { tableData } = state.tableMetadata;
  const { columnLineageMap } = state.lineage;
  const columnStateObject = columnLineageMap[ownProps.columnName];
  const lineage =
    (columnStateObject && columnStateObject.lineageTree) || initialLineageState;
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
