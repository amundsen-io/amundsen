// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';

import { getFilterConfigByResource } from 'config/config-utils';
import { FilterType, SearchFilterInput } from 'interfaces';
import { bindActionCreators } from 'redux';
import {
  updateFilterByCategory,
  UpdateFilterRequest,
} from 'ducks/search/filters/reducer';
import { CheckboxFilterProperties } from './CheckBoxFilter';
import FilterSection from './FilterSection';

import './styles.scss';
import { APPLY_BTN_TEXT, CLEAR_BTN_TEXT } from './constants';

export interface FilterSectionItem {
  categoryId: string;
  helpText?: string;
  title: string;
  type: FilterType;
}

export interface CheckboxFilterSection extends FilterSectionItem {
  options: CheckboxFilterProperties[];
}

export interface StateFromProps {
  filterSections: FilterSectionItem[];
}

interface DispatchFromProps {
  updateFilter: (searchFilters: SearchFilterInput[]) => UpdateFilterRequest;
}

export type SearchFilterProps = StateFromProps & DispatchFromProps;

export class SearchFilter extends React.Component<SearchFilterProps> {
  onApplyChanges = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const form = document.getElementById(
      'input-filters-form'
    ) as HTMLFormElement;
    const formData = new FormData(form);

    const { filterSections, updateFilter } = this.props;
    const filters = filterSections
      .filter(
        (section) =>
          section.type === FilterType.INPUT_SELECT &&
          (formData.get(section.categoryId) as string)
      )
      .map((section) => ({
        categoryId: section.categoryId,
        value: formData.get(section.categoryId) as string,
      }));
    updateFilter(filters);
  };

  onClearFilter = () => {
    const { filterSections, updateFilter } = this.props;
    const filters = filterSections.map((section) => ({
      categoryId: section.categoryId,
      value: undefined,
    }));
    updateFilter(filters);
  };

  createFilterSection = (
    key: string,
    section: FilterSectionItem | CheckboxFilterSection
  ) => {
    const { categoryId, helpText, title, type } = section;
    const options = (section as CheckboxFilterSection).options
      ? (section as CheckboxFilterSection).options
      : undefined;
    return (
      <FilterSection
        key={key}
        categoryId={categoryId}
        helpText={helpText}
        title={title}
        type={type}
        options={options}
      />
    );
  };

  renderFilterSections = (filterSections) =>
    filterSections.map((section) =>
      this.createFilterSection(`section:${section.categoryId}`, section)
    );

  render = () => {
    const { filterSections } = this.props;

    return (
      <div className="search-filter-section">
        {Object.keys(filterSections).length > 0 && (
          <form
            id="input-filters-form"
            className="input-section-content form-group"
            onSubmit={this.onApplyChanges}
          >
            {this.renderFilterSections(filterSections)}
            <div className="input-section-buttons">
              <button
                name="search-filter-apply-btn"
                className="btn btn-default"
                type="submit"
              >
                {APPLY_BTN_TEXT}
              </button>
              <button
                onClick={this.onClearFilter}
                className="btn btn-default"
                type="button"
              >
                {CLEAR_BTN_TEXT}
              </button>
            </div>
          </form>
        )}
      </div>
    );
  };
}

export const mapStateToProps = (state: GlobalState) => {
  const resourceType = state.search.resource;
  const filterCategories = getFilterConfigByResource(resourceType);
  const filterSections: CheckboxFilterSection[] = [];

  if (filterCategories) {
    filterCategories.forEach((categoryConfig) => {
      const section: CheckboxFilterSection = {
        categoryId: categoryConfig.categoryId,
        helpText: categoryConfig.helpText,
        title: categoryConfig.displayName,
        type: categoryConfig.type,
        options: [],
      };
      if (categoryConfig.type === FilterType.CHECKBOX_SELECT) {
        section.options = categoryConfig.options.map(
          ({ value, displayName }) => ({ value, label: displayName || '' })
        );
      }
      filterSections.push(section);
    });
  }

  return {
    filterSections,
  };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      updateFilter: (searchFilters: SearchFilterInput[]) =>
        updateFilterByCategory({ searchFilters }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(SearchFilter);
