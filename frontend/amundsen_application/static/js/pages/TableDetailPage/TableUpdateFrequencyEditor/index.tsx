// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import { updateTableUpdateFrequency, deleteTableUpdateFrequency } from 'ducks/tableMetadata/reducer';

import EditableSelect, {
  ComponentProps,
  DispatchFromProps,
  StateFromProps,
  SelectOption,
  SelectOptionAction
} from 'components/EditableSelect';

export const mapStateToProps = (state: GlobalState) => {

  const noneOption: SelectOption = {
    option: 'none',
    action: SelectOptionAction.DELETE
  };
  const dailyOption: SelectOption = {
    option: 'daily',
    action: SelectOptionAction.UPDATE
  };
  const weeklyOption: SelectOption = {
    option: 'weekly',
    action: SelectOptionAction.UPDATE
  };
  const monthlyOption: SelectOption = {
    option: 'monthly',
    action: SelectOptionAction.UPDATE
  };
  const quarterlyOption: SelectOption = {
    option: 'quarterly',
    action: SelectOptionAction.UPDATE
  };
  const annuallyOption: SelectOption = {
    option: 'annually',
    action: SelectOptionAction.UPDATE
  };

  return {
    refreshValue: state.tableMetadata.tableData.update_frequency,
    options: [noneOption, dailyOption, weeklyOption, monthlyOption, quarterlyOption, annuallyOption],
    defaultOption: 'none'
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ onUpdateValue: updateTableUpdateFrequency, onDeleteValue: deleteTableUpdateFrequency }, dispatch);

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(
  mapStateToProps,
  mapDispatchToProps
)(EditableSelect);


