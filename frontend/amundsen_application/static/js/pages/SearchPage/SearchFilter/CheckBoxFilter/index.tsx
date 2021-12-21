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

import CheckBoxItem from 'components/Inputs/CheckBoxItem';

export interface CheckboxFilterProperties {
  label: string;
  value: string;
}

interface OwnProps {
  categoryId: string;
  checkboxProperties: CheckboxFilterProperties[];
}

interface StateFromProps {
  checkedValues: string[];
}

interface DispatchFromProps {
  applyFilters: (
    categoryId: string,
    checkedValues: string[]
  ) => UpdateFilterRequest;
}

export type CheckBoxFilterProps = OwnProps & DispatchFromProps & StateFromProps;

export class CheckBoxFilter extends React.Component<CheckBoxFilterProps> {
  createCheckBoxItem = (
    categoryId: string,
    key: string,
    item: CheckboxFilterProperties
  ) => {
    const { checkedValues } = this.props;
    const { label, value } = item;
    return (
      <CheckBoxItem
        key={key}
        checked={checkedValues.includes(value)}
        name={categoryId}
        value={value}
        onChange={this.onCheckboxChange}
      >
        <span className="subtitle-2">{label}</span>
      </CheckBoxItem>
    );
  };

  onCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { checkedValues } = this.props;
    const { applyFilters } = this.props;
    const { value } = e.target;
    const categoryId = e.target.name;

    let newCheckedValues;
    if (e.target.checked) {
      newCheckedValues = [...checkedValues, value];
    } else {
      newCheckedValues = checkedValues.filter((item) => item !== value);
    }

    applyFilters(categoryId, newCheckedValues);
  };

  render = () => {
    const { categoryId, checkboxProperties } = this.props;
    return (
      <div className="checkbox-section-content">
        {checkboxProperties.map((item, index) =>
          this.createCheckBoxItem(
            categoryId,
            `item:${categoryId}:${index}`,
            item
          )
        )}
      </div>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const filterValues = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : undefined;
  const value = filterValues ? filterValues.value : '';
  const checkedValues = value ? value.split(',') : [];
  return { checkedValues };
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
)(CheckBoxFilter);
