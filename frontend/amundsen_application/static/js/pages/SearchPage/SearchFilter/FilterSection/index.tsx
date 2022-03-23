// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { FilterType, FilterOperationType, IconSizes } from 'interfaces';
import InfoButton from 'components/InfoButton';

import CheckBoxFilter, { CheckboxFilterProperties } from '../CheckBoxFilter';
import InputFilter from '../InputFilter';
import ToggleFilter from '../ToggleFilter';

export interface FilterSectionProps {
  categoryId: string;
  allowableOperation?: FilterOperationType;
  defaultValue?: string[];
  helpText?: string;
  title: string;
  type: FilterType;
  options?: CheckboxFilterProperties[];
}

const Filter: React.FC<FilterSectionProps> = ({
  categoryId,
  helpText,
  allowableOperation,
  options,
  title,
  type,
}) => {
  if (type === FilterType.INPUT_SELECT) {
    return (
      <InputFilter
        categoryId={categoryId}
        helpText={helpText}
        allowableOperation={allowableOperation}
      />
    );
  }
  if (type === FilterType.CHECKBOX_SELECT) {
    return (
      <CheckBoxFilter
        categoryId={categoryId}
        checkboxProperties={options || []}
      />
    );
  }
  if (type === FilterType.TOGGLE_FILTER) {
    return (
      <ToggleFilter
        categoryId={categoryId}
        filterName={title}
        helpText={helpText}
      />
    );
  }
  return null;
};

const FilterTitle: React.FC<FilterSectionProps> = ({
  categoryId,
  helpText,
  title,
  type,
}) => {
  if (type === FilterType.INPUT_SELECT || type === FilterType.CHECKBOX_SELECT) {
    return (
      <div className="search-filter-section-header">
        <div className="search-filter-section-title">
          <label className="search-filter-section-label" htmlFor={categoryId}>
            {title}
          </label>
          {helpText && type === FilterType.CHECKBOX_SELECT && (
            <InfoButton
              infoText={helpText}
              placement="top"
              size={IconSizes.SMALL}
            />
          )}
        </div>
      </div>
    );
    // else case includes toggle filters
  }
  return null;
};

const FilterSection: React.FC<FilterSectionProps> = ({
  categoryId,
  allowableOperation,
  helpText,
  title,
  type,
  options,
}: FilterSectionProps) => (
  <div className="search-filter-section">
    <FilterTitle
      categoryId={categoryId}
      helpText={helpText}
      title={title}
      type={type}
    />
    <Filter
      categoryId={categoryId}
      helpText={helpText}
      allowableOperation={allowableOperation}
      options={options}
      title={title}
      type={type}
    />
  </div>
);

export default FilterSection;
