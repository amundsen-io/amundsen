import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../../ducks/rootReducer";
import { updateTableOwner } from '../../../ducks/tableMetadata/owners/reducer';

import OwnerEditor, { ComponentProps, DispatchFromProps, StateFromProps } from '../../../components/OwnerEditor';

export const mapStateToProps = (state: GlobalState) => {
  const ownerObj = state.tableMetadata.tableOwners.owners;
  const items = Object.keys(ownerObj).reduce((obj, ownerId) => {
    obj[ownerId] = { label: ownerObj[ownerId].display_name }
    return obj;
  }, {});

  return {
    isLoading: state.tableMetadata.tableOwners.isLoading,
    itemProps: items,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ onUpdateList: updateTableOwner } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(OwnerEditor);
