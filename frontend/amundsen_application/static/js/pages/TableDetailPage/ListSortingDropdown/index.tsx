// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown } from 'react-bootstrap';

import { SortCriteria } from 'interfaces';

import { SORT_BY_DROPDOWN_TITLE, SORT_BY_MENU_TITLE_TEXT } from '../constants';

import './styles.scss';

type Criterias = { [key: string]: SortCriteria };

export interface ListSortingDropdownProps {
  options: Criterias;
  currentSelection?: SortCriteria;
  onChange?: (value) => void;
}

type OptionType = string;

const TableReportsDropdown: React.FC<ListSortingDropdownProps> = ({
  options,
  currentSelection,
  onChange,
}: ListSortingDropdownProps) => {
  const criterias = Object.entries(options);
  const [selectedOption, setSelectedOption] = React.useState<OptionType>(
    currentSelection ? currentSelection.key : criterias?.[0]?.[1]?.key
  );
  const [isOpen, setOpen] = React.useState(false);

  if (criterias.length < 1) {
    return null;
  }

  const handleChange = (e) => {
    const { value } = e.target;

    setSelectedOption(value);
    setOpen(false);
    if (onChange) {
      onChange(value);
    }
  };

  return (
    <Dropdown
      className="list-sorting-dropdown"
      id="list-sorting-dropdown"
      pullRight
      open={isOpen}
      onToggle={() => {
        setOpen(!isOpen);
      }}
    >
      <Dropdown.Toggle className="btn btn-default list-sorting-dropdown-button">
        {SORT_BY_DROPDOWN_TITLE}
      </Dropdown.Toggle>
      <Dropdown.Menu className="list-sorting-dropdown-menu">
        <h5 className="list-sorting-dropdown-menu-title">
          {SORT_BY_MENU_TITLE_TEXT}
        </h5>
        {criterias.map(([_, { key, name }]) => (
          <li key={name}>
            <label className="list-sorting-dropdown-menu-item radio-label">
              <input
                type="radio"
                name="sort-option"
                value={key}
                checked={selectedOption === key}
                onChange={handleChange}
              />
              <span className="list-sorting-dropdown-menu-item-text">
                {name}
              </span>
            </label>
          </li>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default TableReportsDropdown;
