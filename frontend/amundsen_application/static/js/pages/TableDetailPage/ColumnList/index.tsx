// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { OpenRequestAction } from 'ducks/notification/types';

import { TableColumn, RequestMetadataType } from 'interfaces';

import ColumnListItem from '../ColumnListItem';

import './styles.scss';

interface ColumnListProps {
  columns?: TableColumn[];
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName: string
  ) => OpenRequestAction;
  database: string;
  editText?: string;
  editUrl?: string;
}

const ColumnList: React.FC<ColumnListProps> = ({
  columns,
  database,
  editText,
  editUrl,
  openRequestDescriptionDialog,
}: ColumnListProps) => {
  if (columns.length < 1) {
    return <div />;
    // ToDo: return No Results Message
  }

  const columnList = columns.map((entry, index) => (
    <ColumnListItem
      openRequestDescriptionDialog={openRequestDescriptionDialog}
      key={`column:${index}`}
      data={entry}
      database={database}
      index={index}
      editText={editText}
      editUrl={editUrl}
    />
  ));

  return <ul className="column-list list-group">{columnList}</ul>;
};

ColumnList.defaultProps = {
  columns: [] as TableColumn[],
  editText: '',
  editUrl: '',
};

export default ColumnList;
