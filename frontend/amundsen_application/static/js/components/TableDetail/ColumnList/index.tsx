import * as React from 'react';
import ColumnListItem from '../ColumnListItem';

import { TableColumn } from 'interfaces';

import "./styles.scss";


interface ColumnListProps {
  columns?: TableColumn[];
}

// TODO - convert into a component for easier testing
const ColumnList: React.SFC<ColumnListProps> = ({ columns }) => {
  if (columns.length < 1) {
    return (<div />);
    // ToDo: return No Results Message
  }

  const columnList = columns.map((entry, index) =>
    <ColumnListItem
      key={`column:${index}`}
      data={ entry }
      index={ index }
    />);

  return (
    <ul className="column-list list-group">
      { columnList }
    </ul>
  );
};

ColumnList.defaultProps = {
  columns: [] as TableColumn[],
};

export default ColumnList;
