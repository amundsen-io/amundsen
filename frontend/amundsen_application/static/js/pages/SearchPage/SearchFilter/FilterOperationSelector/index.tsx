// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { ToggleButton, ToggleButtonGroup } from 'react-bootstrap';

import { FilterOperationType } from 'interfaces/Enums';
import { logClick } from 'utils/analytics';
import { AND_LABEL, OR_LABEL } from '../constants';
import '../styles.scss';

export interface FilterOperationSelectorProps {
  filterOperation: FilterOperationType;
  handleFilterOperationChange: (newOperation: FilterOperationType) => void;
  allowableOperation?: FilterOperationType;
  categoryId: string;
}

const handleClick = (categoryId, e) => {
  logClick(e, {
    target_id: 'search_filter_operation_selector',
    value: categoryId,
  });
};

const FilterOperationSelector: React.FC<FilterOperationSelectorProps> = ({
  filterOperation,
  handleFilterOperationChange,
  allowableOperation,
  categoryId,
}: FilterOperationSelectorProps) => (
  <div className="filter-operation-toggle">
    <ToggleButtonGroup
      type="radio"
      name={categoryId + 'Selector'}
      id={categoryId + 'Selector'}
      value={filterOperation}
      onChange={handleFilterOperationChange}
    >
      <ToggleButton
        value={FilterOperationType.AND}
        disabled={allowableOperation === FilterOperationType.OR}
        onClick={handleClick.bind(null, categoryId)}
      >
        {AND_LABEL}
      </ToggleButton>
      <ToggleButton
        value={FilterOperationType.OR}
        disabled={allowableOperation === FilterOperationType.AND}
        onClick={handleClick.bind(null, categoryId)}
      >
        {OR_LABEL}
      </ToggleButton>
    </ToggleButtonGroup>
  </div>
);

export default FilterOperationSelector;
