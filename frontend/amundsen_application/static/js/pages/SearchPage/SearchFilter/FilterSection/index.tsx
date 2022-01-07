// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { FilterType, FilterOperationType, IconSizes } from 'interfaces';
import InfoButton from 'components/InfoButton';

import CheckBoxFilter, { CheckboxFilterProperties } from '../CheckBoxFilter';
import InputFilter from '../InputFilter';

export interface FilterSectionProps {
  categoryId: string;
  allowableOperation?: FilterOperationType;
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
    {getFilterComponent(
      categoryId,
      helpText,
      allowableOperation,
      options,
      type
    )}
  </div>
);

export default FilterSection;
