import * as React from 'react';
import { TableColumn } from 'interfaces';
import ColumnListItem from '../ColumnListItem';

import './styles.scss';

interface ColumnListProps {
  columns?: TableColumn[];
}

const ColumnList: React.SFC<ColumnListProps> = ({
  columns,
}: ColumnListProps) => {
  if (columns.length < 1) {
    return <div />;
    // ToDo: return No Results Message
  }

  const columnList = columns.map((entry, index) => (
    <ColumnListItem key={`column:${index}`} data={entry} index={index} />
  ));

  return <ul className="column-list list-group">{columnList}</ul>;
};

ColumnList.defaultProps = {
  columns: [] as TableColumn[],
};

export default ColumnList;
