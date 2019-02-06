import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { updateTableOwner, UpdateMethod } from '../../../ducks/tableMetadata/reducer';

import EditableList, { ComponentProps, DispatchFromProps } from '../../../components/common/EditableList';

function onAddItem(value, onSuccess, onFailure) {
  return updateTableOwner(value, UpdateMethod.PUT, onSuccess, onFailure);
}

function onDeleteItem(value, onSuccess, onFailure) {
  return updateTableOwner(value, UpdateMethod.DELETE, onSuccess, onFailure);
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ onAddItem, onDeleteItem } , dispatch);
};

export default connect<{}, DispatchFromProps, ComponentProps>(null, mapDispatchToProps)(EditableList);
