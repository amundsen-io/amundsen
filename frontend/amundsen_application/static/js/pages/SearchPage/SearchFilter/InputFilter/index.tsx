// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import {
  updateFilterByCategory,
  UpdateFilterRequest,
} from 'ducks/search/filters/reducer';

import { GlobalState } from 'ducks/rootReducer';
import { APPLY_BTN_TEXT } from '../constants';

interface OwnProps {
  categoryId: string;
}

interface StateFromProps {
  values: string[];
  operation: string;
}

interface DispatchFromProps {
  updateFilter: (
    categoryId: string,
    values: string[],
    operation: string,
  ) => UpdateFilterRequest;
}

export type InputFilterProps = StateFromProps & DispatchFromProps & OwnProps;

export interface InputFilterState {
  values: string[];
  operation: string;
}

export class InputFilter extends React.Component<
  InputFilterProps,
  InputFilterState
> {
  constructor(props) {
    super(props);

    this.state = {
      values: props.values,
      operation: props.operation,
    };
  }

  componentDidUpdate = (prevProps: StateFromProps) => {
    const newValue = this.props.values;
    if (prevProps.values !== newValue) {
      this.setState({ values: newValue || [] });
    }
  };

  onApplyChanges = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (this.state.values) {
      // TODO change operation when available in FE component
      this.props.updateFilter(this.props.categoryId, this.state.values, 'OR');
    } else {
      this.props.updateFilter(this.props.categoryId, [], 'OR');
    }
  };

  onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ values: [e.target.value.toLowerCase()] });
  };

  render = () => {
    const { categoryId } = this.props;
    return (
      <form
        className="input-section-content form-group"
        onSubmit={this.onApplyChanges}
      >
        <input
          type="text"
          className="form-control"
          name={categoryId}
          id={categoryId}
          onChange={this.onInputChange}
          value={this.state.values}
        />
        <button name={categoryId} className="btn btn-default" type="submit">
          {APPLY_BTN_TEXT}
        </button>
      </form>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;

  const values = filterState[ownProps.categoryId]? 
    filterState[ownProps.categoryId].values
    : [];
  const operation = filterState[ownProps.categoryId]? 
  filterState[ownProps.categoryId].operation
  : 'OR';
  return {
    values: values || [],
    operation: operation || 'OR',
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      updateFilter: (categoryId: string, values: string[], operation: string) =>
        updateFilterByCategory({ categoryId, values, operation }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps, OwnProps>(
  mapStateToProps,
  mapDispatchToProps
)(InputFilter);
