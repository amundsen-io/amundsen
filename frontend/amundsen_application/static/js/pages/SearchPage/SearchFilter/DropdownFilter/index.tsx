import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import Select from 'react-select';

import { GlobalState } from 'ducks/rootReducer';
import {
  updateFilterByCategory,
  UpdateFilterRequest,
} from 'ducks/search/filters/reducer';

export interface DropdownOptions {
  label: string;
  value: string;
}

interface OwnProps {
  categoryId: string;
  dropdownProperties: DropdownOptions[];
}

interface SelectedOptions {
  label: string;
  value: string;
}
interface StateFromProps {
  selectedOptions: Array<SelectedOptions>;
}

interface DispatchFromProps {
  applyFilters: (
    categoryId: string,
    checkedValues: string[]
  ) => UpdateFilterRequest;
}

export type DropDownFilterProps = OwnProps & DispatchFromProps & StateFromProps;

export class DropDownFilter extends React.Component<DropDownFilterProps> {
  onSelectUpdate = (options) => {
    const { categoryId } = this.props;
    // let checkedValues = {};
    const checkedValues = [] as any;
    options.map((eachOption) => {
      checkedValues.push(eachOption.value);
    });
    if (Object.keys(checkedValues).length === 0) {
      this.props.applyFilters(categoryId, []);
    } else {
      this.props.applyFilters(categoryId, checkedValues);
    }
  };

  transformOptions = (options) => {
    if (options.length) {
      const transformedOptions = options[0].value
        .split(',')
        .map((eachValue) => ({ value: eachValue, label: eachValue }));
      return transformedOptions;
    }
    return [];
  };

  render = () => {
    const { categoryId, dropdownProperties } = this.props;
    return (
      <div className="checkbox-section-content">
        <Select
          closeMenuOnSelect={false}
          onChange={this.onSelectUpdate}
          isMulti
          name={categoryId}
          value={this.transformOptions(this.props.selectedOptions)}
          options={dropdownProperties}
        />
      </div>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const filterValues = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : [];
  let selectedOptions: Array<{ label: string; value: string }> = [];

  if (filterValues) {
    selectedOptions = Object.keys(filterValues).map((eachKey) => ({
      label: filterValues[eachKey],
      value: filterValues[eachKey],
    }));
  }

  return {
    selectedOptions,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      applyFilters: (categoryId: string, checkedValues: string[]) =>
        updateFilterByCategory({
          searchFilters: [{ categoryId, value: checkedValues || undefined }],
        }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps, OwnProps>(
  mapStateToProps,
  mapDispatchToProps
)(DropDownFilter);
