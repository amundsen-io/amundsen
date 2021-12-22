// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { updateSearchState } from 'ducks/search/reducer';
import { FilterOperationType } from 'interfaces/Enums';
import { ResourceType } from 'interfaces/Resources';
import { UpdateSearchStateRequest } from 'ducks/search/types';
import { FilterReducerState } from 'ducks/search/filters/reducer';
import FilterOperationSelector from '../FilterOperationSelector';
import '../styles.scss';

interface OwnProps {
  categoryId: string;
  allowableOperation?: FilterOperationType;
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

const getFilterObject = (filterState, resourceType, categoryId) =>
  filterState[resourceType] ? filterState[resourceType][categoryId] : undefined;

export class InputFilter extends React.Component<
  InputFilterProps,
  InputFilterState
> {
  constructor(props) {
    super(props);

    this.state = {
      value: props.value,
      filterOperation: props.filterOperation,
      showFilterOperationToggle: props.value.includes(','),
    };
  }

  componentDidUpdate = (prevProps: StateFromProps) => {
    const { value: newValue, filterOperation: newFilterOperation } = this.props;
    if (prevProps.value !== newValue) {
      const showFilterOp = newValue.includes(',');
      this.setState({
        value: newValue || '',
        showFilterOperationToggle: showFilterOp,
        filterOperation: newFilterOperation,
      });
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

    const showFilterOperationToggle = newValue.includes(',');
    this.setState({ value: newValue, showFilterOperationToggle });

    let newFilters;
    if (newValue) {
      const currentFilter = getFilterObject(
        filterState,
        resourceType,
        categoryId
      );
      const hasFilterOperation = currentFilter && currentFilter.filterOperation;
      const newFilter = hasFilterOperation
        ? { value: newValue, filterOperation: currentFilter.filterOperation }
        : { value: newValue };

      newFilters = {
        ...filterState,
        [resourceType]: {
          ...filterState[resourceType],
          [categoryId]: newFilter,
        },
      };
    } else {
      // Remove the categoryId from the filters if the new value is empty
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { [categoryId]: _, ...updatedResourceFilters } = filterState[
        resourceType
      ];

      newFilters = {
        ...filterState,
        [resourceType]: updatedResourceFilters,
      };
    }

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

    const currentFilter = getFilterObject(
      filterState,
      resourceType,
      categoryId
    );
    const hasValue = currentFilter && currentFilter.value;
    const newFilter = hasValue
      ? { value: currentFilter.value, filterOperation: newOperation }
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
    const { categoryId, allowableOperation } = this.props;
    const inputAriaLabel = categoryId + 'FilterInput';
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
          <FilterOperationSelector
            filterOperation={filterOperation}
            handleFilterOperationChange={this.handleFilterOperationChange}
            allowableOperation={allowableOperation}
            categoryId={categoryId}
          />
        )}
      </div>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const inputFilter = getFilterObject(
    state.search.filters,
    state.search.resource,
    ownProps.categoryId
  );
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
