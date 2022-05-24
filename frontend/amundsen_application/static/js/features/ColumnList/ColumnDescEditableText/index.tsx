// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import {
  getColumnDescription,
  updateColumnDescription,
} from 'ducks/tableMetadata/reducer';

import EditableText, {
  ComponentProps,
  DispatchFromProps,
  StateFromProps,
} from 'components/EditableText';

interface ContainerOwnProps {
  columnName: string;
}

export const mapStateToProps = (
  state: GlobalState,
  ownProps: ContainerOwnProps
) => ({
  refreshValue: state.tableMetadata.tableData.columns.find(
    (column) => column.name === ownProps.columnName
  )?.description,
});

export const mapDispatchToProps = (
  dispatch: any,
  ownProps: ContainerOwnProps
) => {
  const getLatestValue = function (onSuccess, onFailure) {
    return getColumnDescription(ownProps.columnName, onSuccess, onFailure);
  };
  const onSubmitValue = function (newValue, onSuccess, onFailure) {
    return updateColumnDescription(
      newValue,
      ownProps.columnName,
      onSuccess,
      onFailure
    );
  };

  return bindActionCreators({ getLatestValue, onSubmitValue }, dispatch);
};

export default connect<
  StateFromProps,
  DispatchFromProps,
  ComponentProps & ContainerOwnProps
>(
  mapStateToProps,
  mapDispatchToProps
)(EditableText);
