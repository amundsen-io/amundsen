// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { FilterType, IconSizes } from 'interfaces';
import InfoButton from 'components/InfoButton';

import CheckBoxFilter, { CheckboxFilterProperties } from '../CheckBoxFilter';
import InputFilter from '../InputFilter';

export interface OwnProps {
  categoryId: string;
  helpText?: string;
  title: string;
  type: FilterType;
  options?: CheckboxFilterProperties[];
  setDidApplyFilters: (didApply: boolean) => void;
}

export interface StateFromProps {
  hasValue: boolean;
}

export type FilterSectionProps = OwnProps & StateFromProps;

export class FilterSection extends React.Component<FilterSectionProps> {
  renderFilterComponent = () => {
    const { categoryId, options, type, setDidApplyFilters } = this.props;

    if (type === FilterType.INPUT_SELECT) {
      return <InputFilter categoryId={categoryId} />;
    }
    if (type === FilterType.CHECKBOX_SELECT) {
      return (
        <CheckBoxFilter
          categoryId={categoryId}
          checkboxProperties={options || []}
          setDidApplyFilters={setDidApplyFilters}
        />
      );
    }
  };

  render = () => {
    const { categoryId, helpText, title } = this.props;

    return (
      <div className="search-filter-section">
        <div className="search-filter-section-header">
          <div className="search-filter-section-title">
            <label
              className="search-filter-section-label title-2"
              htmlFor={categoryId}
            >
              {title}
            </label>
            {helpText && (
              <InfoButton
                infoText={helpText}
                placement="top"
                size={IconSizes.SMALL}
              />
            )}
          </div>
        </div>
        {this.renderFilterComponent()}
      </div>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const filterValue = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : null;
  let hasValue = false;
  if (filterValue && ownProps.type === FilterType.CHECKBOX_SELECT) {
    Object.keys(filterValue).forEach((key) => {
      if (filterValue[key] === true) {
        hasValue = true;
      }
    });
  } else if (ownProps.type === FilterType.INPUT_SELECT) {
    hasValue = !!filterValue;
  }

  return {
    hasValue,
  };
};

export default connect<StateFromProps, OwnProps>(mapStateToProps)(
  FilterSection
);
