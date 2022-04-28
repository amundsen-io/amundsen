// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';

import { getFilterConfigByResource } from 'config/config-utils';
import { FilterType, FilterOperationType, SearchFilterInput } from 'interfaces';
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
  allowableOperation?: FilterOperationType;
  helpText?: string;
  title: string;
  type: FilterType;
  defaultValue?: string[];
}

export interface CheckboxFilterSection extends FilterSectionItem {
  options: CheckboxFilterProperties[];
}

export interface StateFromProps {
  filterSections: FilterSectionItem[];
}

interface DispatchFromProps {
  applyFilters: () => UpdateFilterRequest;
  clearFilters: (searchFilters: SearchFilterInput[]) => UpdateFilterRequest;
}

export type SearchFilterProps = StateFromProps & DispatchFromProps;

export class SearchFilter extends React.Component<SearchFilterProps> {
  onApplyChanges = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const { applyFilters } = this.props;
    applyFilters();
  };

  onClearFilter = () => {
    const { filterSections, clearFilters } = this.props;
    const filters = filterSections.map((section) => ({
      categoryId: section.categoryId,
      value: undefined,
    }));
    clearFilters(filters);
  };

  createFilterSection = (
    key: string,
    section: FilterSectionItem | CheckboxFilterSection
  ) => {
    const {
      categoryId,
      allowableOperation,
      helpText,
      title,
      defaultValue,
      type,
    } = section;
    const options = (section as CheckboxFilterSection).options
      ? (section as CheckboxFilterSection).options
      : undefined;
    return (
      <FilterSection
        key={key}
        categoryId={categoryId}
        allowableOperation={allowableOperation}
        helpText={helpText}
        title={title}
        defaultValue={defaultValue}
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
        allowableOperation: categoryConfig.allowableOperation,
        helpText: categoryConfig.helpText,
        title: categoryConfig.displayName,
        type: categoryConfig.type,
        defaultValue: categoryConfig.defaultValue,
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
      applyFilters: () => updateFilterByCategory({ searchFilters: [] }),
      clearFilters: (searchFilters: SearchFilterInput[]) =>
        updateFilterByCategory({ searchFilters }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(SearchFilter);
