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

const getFilterComponent = (
  categoryId,
  helpText,
  allowableOperation,
  options,
  defaultValue,
  title,
  type
) => {
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
};

const getFilterTitleComponent = (categoryId, helpText, title, type) => {
  if (type === FilterType.INPUT_SELECT || type === FilterType.CHECKBOX_SELECT) {
    return (
      <div className="search-filter-section-header">
        <div className="search-filter-section-title">
          <label
            className="search-filter-section-label title-2"
            htmlFor={categoryId}
          >
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
  }
  if (type === FilterType.TOGGLE_FILTER) {
    return null;
  }
};

const FilterSection: React.FC<FilterSectionProps> = ({
  categoryId,
  allowableOperation,
  helpText,
  title,
  type,
  options,
  defaultValue,
}: FilterSectionProps) => (
  <div className="search-filter-section">
    {getFilterTitleComponent(categoryId, helpText, title, type)}
    {getFilterComponent(
      categoryId,
      helpText,
      allowableOperation,
      options,
      defaultValue,
      title,
      type
    )}
  </div>
);

export default FilterSection;
