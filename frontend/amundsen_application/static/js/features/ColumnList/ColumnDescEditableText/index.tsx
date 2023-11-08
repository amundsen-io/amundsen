// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import {
  getColumnDescription,
  updateColumnDescription,
  getTypeMetadataDescription,
  updateTypeMetadataDescription,
} from 'ducks/tableMetadata/reducer';
import { getTypeMetadataFromKey } from 'ducks/tableMetadata/api/helpers';
import {
  getGPTResponse
} from 'ducks/ai/reducer';

import EditableText, {
  ComponentProps,
  DispatchFromProps,
  StateFromProps,
} from 'components/EditableText';

export interface ContainerOwnProps {
  columnKey: string;
  isNestedColumn: boolean;
}

export const mapStateToProps = (
  state: GlobalState,
  ownProps: ContainerOwnProps
) => ({
  refreshValue: !ownProps.isNestedColumn
    ? state.tableMetadata.tableData.columns.find(
        (column) => column.key === ownProps.columnKey
      )?.description
    : getTypeMetadataFromKey(ownProps.columnKey, state.tableMetadata.tableData)
        ?.description,
  gptResponse: state.gptResponse.gptResponse
});

export const mapDispatchToProps = (
  dispatch: any,
  ownProps: ContainerOwnProps
) => {
  const getLatestValue = function (onSuccess, onFailure) {
    return !ownProps.isNestedColumn
      ? getColumnDescription(ownProps.columnKey, onSuccess, onFailure)
      : getTypeMetadataDescription(ownProps.columnKey, onSuccess, onFailure);
  };
  const onSubmitValue = function (newValue, onSuccess, onFailure) {
    return !ownProps.isNestedColumn
      ? updateColumnDescription(
          newValue,
          ownProps.columnKey,
          onSuccess,
          onFailure
        )
      : updateTypeMetadataDescription(
          newValue,
          ownProps.columnKey,
          onSuccess,
          onFailure
        );
  };

  return bindActionCreators({ getLatestValue, onSubmitValue, getGPTResponse: getGPTResponse }, dispatch);
};

export default connect<
  StateFromProps,
  DispatchFromProps,
  ComponentProps & ContainerOwnProps
>(
  mapStateToProps,
  mapDispatchToProps
)(EditableText);
