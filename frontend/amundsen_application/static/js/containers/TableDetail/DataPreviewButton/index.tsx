import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../../ducks/rootReducer";

import DataPreviewButton, { ComponentProps, StateFromProps, getStatusFromCode } from '../../../components/TableDetail/DataPreviewButton';

export const mapStateToProps = (state: GlobalState) => {
  return {
    previewData: state.tableMetadata.preview.data,
    status: getStatusFromCode(state.tableMetadata.preview.status),
  };
};

export default connect<StateFromProps, {}, ComponentProps>(mapStateToProps, null)(DataPreviewButton);
