import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../ducks/rootReducer";
import { getPreviewData, getTableData } from '../../ducks/tableMetadata/reducer';

import TableDetail, { DispatchFromProps, StateFromProps } from '../../components/TableDetail';

export const mapStateToProps = (state: GlobalState) => {
  return {
    isLoading: state.tableMetadata.isLoading,
    statusCode: state.tableMetadata.statusCode,
    tableData: state.tableMetadata.tableData,
    tableOwners: state.tableMetadata.tableOwners,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getPreviewData, getTableData } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(TableDetail);
