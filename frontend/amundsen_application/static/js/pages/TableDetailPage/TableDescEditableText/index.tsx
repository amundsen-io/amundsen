// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import {
  getTableDescription,
  updateTableDescription,
} from 'ducks/tableMetadata/reducer';
import {
  getGPTResponse
} from 'ducks/ai/reducer';

import EditableText, {
  ComponentProps,
  DispatchFromProps,
  StateFromProps,
} from 'components/EditableText';

export const mapStateToProps = (state: GlobalState) => ({
  refreshValue: state.tableMetadata.tableData.description,
  gptResponse: state.gptResponse.gptResponse
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      getLatestValue: getTableDescription,
      onSubmitValue: updateTableDescription,
      getGPTResponse: getGPTResponse
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(EditableText);
