// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import {
  updateFilterByCategory,
  UpdateFilterRequest,
} from 'ducks/search/filters/reducer';

import InfoButton from 'components/InfoButton';

import ToggleSwitch from 'components/ToggleSwitch/ToggleSwitch';

import './styles.scss';

interface OwnProps {
  categoryId: string;
  filterName: string;
  helpText: string;
}

interface StateFromProps {
  checked: boolean;
}

interface DispatchFromProps {
  applyFilters: (categoryId: string, value: string[]) => UpdateFilterRequest;
}
// TODO change to FC

export type ToggleFilterProps = OwnProps & DispatchFromProps & StateFromProps;

export class ToggleFilter extends React.Component<ToggleFilterProps> {
  constructor(props) {
    const { checked } = props;
    super(props);
    this.state = { checked };
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange = (checked) => {
    this.setState({ checked });
    const { categoryId, applyFilters } = this.props;
    applyFilters(categoryId, [checked.toString()]);
  };

  render = () => {
    const { helpText, filterName } = this.props;
    const { checked } = this.state;
    return (
      <label className="toggle-filter">
        <span className="title-2">{filterName}</span>
        <InfoButton infoText={helpText} />
        <ToggleSwitch checked={checked} onChange={this.handleChange} />
      </label>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const filterValues = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : undefined;
  const value = filterValues ? filterValues.value : '';
  return { value };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      applyFilters: (categoryId: string, value: string[]) =>
        updateFilterByCategory({
          searchFilters: [{ categoryId, value: value || undefined }],
        }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps, OwnProps>(
  mapStateToProps,
  mapDispatchToProps
)(ToggleFilter);
