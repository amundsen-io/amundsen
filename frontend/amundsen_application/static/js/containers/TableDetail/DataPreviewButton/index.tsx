import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../../ducks/rootReducer";
import { getPreviewData } from '../../../ducks/preview/reducer';

import DataPreviewButton, { ComponentProps, DispatchFromProps, StateFromProps, getStatusFromCode } from '../../../components/TableDetail/DataPreviewButton';

export const mapStateToProps = (state: GlobalState) => {
  return {
    previewData: state.preview.previewData,
    status: getStatusFromCode(state.preview.status),
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getPreviewData } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(DataPreviewButton);
