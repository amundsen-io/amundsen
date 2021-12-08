// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { updateSearchState } from 'ducks/search/reducer';
import { ResourceType } from 'interfaces/Resources';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { FilterReducerState } from 'ducks/search/filters/reducer';

interface OwnProps {
  categoryId: string;
}

interface StateFromProps {
  value: string;
  filterState: FilterReducerState;
  resourceType: ResourceType;
}

export interface DispatchFromProps {
  updateFilterState: (
    newFilterState: FilterReducerState
  ) => UpdateSearchStateRequest;
}

export type InputFilterProps = StateFromProps & DispatchFromProps & OwnProps;

export interface InputFilterState {
  value: string;
}

export class InputFilter extends React.Component<
  InputFilterProps,
  InputFilterState
> {
  constructor(props) {
    super(props);

    this.state = {
      value: props.value,
    };
  }

  componentDidUpdate = (prevProps: StateFromProps) => {
    const { value: newValue } = this.props;
    if (prevProps.value !== newValue) {
      this.setState({ value: newValue || '' });
    }
  };

  onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const {
      filterState,
      resourceType,
      categoryId,
      updateFilterState,
    } = this.props;
    const newValue = e.target.value.toLowerCase();

    this.setState({ value: newValue });

    const newFilters = {
      ...filterState,
      [resourceType]: { ...filterState[resourceType], [categoryId]: newValue },
    };
    updateFilterState(newFilters);
  };

  render = () => {
    const { value } = this.state;
    const { categoryId } = this.props;
    const ariaLabel = categoryId + ' filter input';
    return (
      <input
        type="text"
        className="form-control"
        name={categoryId}
        id={categoryId}
        onChange={this.onInputChange}
        value={value}
        aria-label={ariaLabel}
      />
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const value = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : '';
  return {
    value: value || '',
    filterState: state.search.filters,
    resourceType: state.search.resource,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      updateFilterState: (newFilterState: FilterReducerState) =>
        updateSearchState({
          filters: {
            ...newFilterState,
          },
          submitSearch: false,
        }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps, OwnProps>(
  mapStateToProps,
  mapDispatchToProps
)(InputFilter);
