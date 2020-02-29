import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { clearFilterByCategory, updateFilterByCategory, ClearFilterRequest, UpdateFilterRequest, FilterOptions } from 'ducks/search/filters/reducer';

import CheckBoxItem from 'components/common/Inputs/CheckBoxItem';

export interface CheckboxFilterProperties {
  label: string;
  value: string;
}

interface OwnProps {
  categoryId: string;
  checkboxProperties: CheckboxFilterProperties[];
}

interface StateFromProps {
  checkedValues: FilterOptions;
}

interface DispatchFromProps {
  clearFilterByCategory: (categoryId: string) => ClearFilterRequest;
  updateFilterByCategory: (categoryId: string, value: FilterOptions) => UpdateFilterRequest;
}

export type CheckBoxFilterProps = OwnProps & DispatchFromProps & StateFromProps;

export class CheckBoxFilter extends React.Component<CheckBoxFilterProps> {
  constructor(props) {
    super(props);
  }

  createCheckBoxItem = (categoryId: string, key: string, item: CheckboxFilterProperties) => {
    const { label, value } = item;
    return (
      <CheckBoxItem
        key={key}
        checked={ this.props.checkedValues[value] }
        name={ categoryId }
        value={ value }
        onChange={ this.onCheckboxChange }>
          <span className="subtitle-2">{ label }</span>
      </CheckBoxItem>
    );
  };

  onCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let checkedValues = this.props.checkedValues;
    const value = e.target.value;
    const categoryId = e.target.name;

    if (e.target.checked) {
      checkedValues = {
        ...this.props.checkedValues,
        [value]: true,
      }
    } else {
      /* Removing an object key with object destructuring */
      const { [value]: removed, ...newCheckedValues } = this.props.checkedValues;
      checkedValues = newCheckedValues;
    }

    if (Object.keys(checkedValues).length === 0) {
      this.props.clearFilterByCategory(categoryId);
    }
    else {
      this.props.updateFilterByCategory(categoryId, checkedValues);
    }
  };

  render = () => {
    const { categoryId, checkboxProperties } = this.props;
    return (
      <div className="checkbox-section-content">
        { checkboxProperties.map((item, index) => this.createCheckBoxItem(categoryId, `item:${categoryId}:${index}`, item)) }
      </div>
    )
  }
};

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  let filterValues = filterState[state.search.selectedTab] ? filterState[state.search.selectedTab][ownProps.categoryId] : {};
  if (!filterValues) {
    filterValues = {};
  }

  return {
    checkedValues: filterValues
  }
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({
    clearFilterByCategory,
    updateFilterByCategory,
  }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps, OwnProps>(mapStateToProps, mapDispatchToProps)(CheckBoxFilter);
