import * as React from 'react';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';

import { CheckboxFilterProperties } from './CheckBoxFilter';
import FilterSection from './FilterSection';

import { getFilterConfigByResource } from 'config/config-utils';

import { FilterType, ResourceType } from 'interfaces';

import './styles.scss'

export interface FilterSection {
  categoryId: string;
  helpText?: string;
  title: string;
  type: FilterType;
}

export interface CheckboxFilterSection extends FilterSection {
  options: CheckboxFilterProperties[];
}

export interface StateFromProps {
  filterSections: FilterSection[];
}

export type SearchFilterProps = StateFromProps;

export class SearchFilter extends React.Component<SearchFilterProps> {
  createFilterSection = (key: string, section: FilterSection | CheckboxFilterSection) => {
    const { categoryId, helpText, title, type } = section;
    const options = (section as CheckboxFilterSection).options ? (section as CheckboxFilterSection).options : undefined;
    return (
      <FilterSection
        key={key}
        categoryId={ categoryId }
        helpText={ helpText }
        title={ title }
        type={ type }
        options={ options }
      />
    )
  };

  renderFilterSections = () => {
    return this.props.filterSections.map((section) => this.createFilterSection(`section:${section.categoryId}`, section));
  };

  render = () => {
    return (
      <>
        { this.renderFilterSections() }
      </>
    )
  };
};

export const mapStateToProps = (state: GlobalState) => {
  const resourceType = state.search.resource;
  const filterCategories = getFilterConfigByResource(resourceType);

  const filterSections = [];
  if (filterCategories) {
    filterCategories.forEach((categoryConfig) => {
      const section = {
        categoryId: categoryConfig.categoryId,
        helpText: categoryConfig.helpText,
        title: categoryConfig.displayName,
        type: categoryConfig.type,
      }
      if (categoryConfig.type === FilterType.CHECKBOX_SELECT) {
        section['options'] = categoryConfig.options.map((option) => {
          return { value: option.value, label: option.displayName }
        });
      }
      filterSections.push(section);
    });
  }

  return {
    filterSections,
  };
};

export default connect<StateFromProps>(mapStateToProps, null)(SearchFilter);
