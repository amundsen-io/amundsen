// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { ToggleButton, ToggleButtonGroup } from 'react-bootstrap';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { updateSearchState } from 'ducks/search/reducer';
import { FilterOperationType } from 'interfaces/Enums';
import { ResourceType } from 'interfaces/Resources';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { FilterReducerState } from 'ducks/search/filters/reducer';
import { AND_LABEL, OR_LABEL } from '../constants';
import '../styles.scss';

interface OwnProps {
  categoryId: string;
  multiValueSelection: boolean;
}

interface StateFromProps {
  value: string;
  filterOperation: FilterOperationType;
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
  filterOperation: FilterOperationType;
  showFilterOperationToggle: boolean;
}

export class InputFilter extends React.Component<
  InputFilterProps,
  InputFilterState
> {
  constructor(props) {
    super(props);

    this.state = {
      value: props.value,
      filterOperation: props.filterOperation,
      showFilterOperationToggle: false,
    };
  }

  componentDidUpdate = (prevProps: StateFromProps) => {
    const { value: newValue, filterOperation: newFilterOperation } = this.props;
    if (prevProps.value !== newValue) {
      const showFilterOp = newValue.includes(',');
      this.setState({
        value: newValue || '',
        showFilterOperationToggle: showFilterOp,
      });
    }
    if (prevProps.filterOperation !== newFilterOperation) {
      this.setState({ filterOperation: newFilterOperation });
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

    if (newValue.includes(',')) {
      this.setState({ value: newValue, showFilterOperationToggle: true });
    } else {
      this.setState({ value: newValue, showFilterOperationToggle: false });
    }

    const resourceFilter = filterState[resourceType];
    const inputFilter = resourceFilter ? resourceFilter[categoryId] : undefined;
    const prevFilterOperation = inputFilter
      ? inputFilter.filterOperation
      : undefined;
    const newFilter = prevFilterOperation
      ? { value: newValue || undefined, filterOperation: prevFilterOperation }
      : { value: newValue || undefined };

    const newFilters = {
      ...filterState,
      [resourceType]: {
        ...filterState[resourceType],
        [categoryId]: newFilter,
      },
    };
    updateFilterState(newFilters);
  };

  handleFilterOperationChange = (newOperation) => {
    const {
      filterState,
      resourceType,
      categoryId,
      updateFilterState,
    } = this.props;

    this.setState({ filterOperation: newOperation });

    const resourceFilter = filterState[resourceType];
    const inputFilter = resourceFilter ? resourceFilter[categoryId] : undefined;
    const prevValue = inputFilter ? inputFilter.value : undefined;
    const newFilter = prevValue
      ? { value: prevValue, filterOperation: newOperation }
      : { filterOperation: newOperation };

    const newFilters = {
      ...filterState,
      [resourceType]: {
        ...filterState[resourceType],
        [categoryId]: newFilter,
      },
    };
    updateFilterState(newFilters);
  };

  render = () => {
    const { value, filterOperation, showFilterOperationToggle } = this.state;
    const { categoryId, multiValueSelection } = this.props;
    const inputAriaLabel = categoryId + 'FilterInput';
    const toggleGroupId = categoryId + 'Toggle';
    return (
      <div>
        <input
          type="text"
          className="form-control"
          name={categoryId}
          id={categoryId}
          onChange={this.onInputChange}
          value={value}
          aria-label={inputAriaLabel}
        />
        {showFilterOperationToggle && (
          <div className="filter-operation-toggle">
            <ToggleButtonGroup
              type="radio"
              name={toggleGroupId}
              id={toggleGroupId}
              value={filterOperation}
              onChange={this.handleFilterOperationChange}
            >
              <ToggleButton
                value={FilterOperationType.AND}
                disabled={!multiValueSelection}
              >
                {AND_LABEL}
              </ToggleButton>
              <ToggleButton value={FilterOperationType.OR}>
                {OR_LABEL}
              </ToggleButton>
            </ToggleButtonGroup>
          </div>
        )}
      </div>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const inputFilter = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : undefined;
  const value = inputFilter ? inputFilter.value : '';
  const filterOperation = inputFilter
    ? inputFilter.filterOperation
    : FilterOperationType.OR;
  return {
    value: value || '',
    filterOperation: filterOperation || FilterOperationType.OR,
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
