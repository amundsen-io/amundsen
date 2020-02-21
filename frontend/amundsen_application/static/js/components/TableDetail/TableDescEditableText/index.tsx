import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import { getTableDescription, updateTableDescription } from 'ducks/tableMetadata/reducer';

import EditableText, { ComponentProps, DispatchFromProps, StateFromProps } from 'components/common/EditableText';

export const mapStateToProps = (state: GlobalState) => {
  return {
    refreshValue: state.tableMetadata.tableData.description,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getLatestValue: getTableDescription, onSubmitValue: updateTableDescription } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(EditableText);
