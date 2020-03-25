import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { updateFilterByCategory, UpdateFilterRequest } from 'ducks/search/filters/reducer';

import { CLEAR_BTN_TEXT } from '../constants';

import { GlobalState } from 'ducks/rootReducer';

import CheckBoxFilter, { CheckboxFilterProperties } from '../CheckBoxFilter';
import InputFilter from '../InputFilter';

import { FilterType } from 'interfaces';

import InfoButton from 'components/common/InfoButton';

export interface OwnProps {
  categoryId: string;
  helpText?: string;
  title: string;
  type: FilterType;
  options?: CheckboxFilterProperties[];
};

export interface StateFromProps {
  hasValue: boolean;
};

export interface DispatchFromProps {
  clearFilter: (categoryId: string) => UpdateFilterRequest;
};

export type FilterSectionProps = OwnProps & DispatchFromProps & StateFromProps;

export class FilterSection extends React.Component<FilterSectionProps> {
  constructor(props) {
    super(props);
  }

  onClearFilter = () => {
    this.props.clearFilter(this.props.categoryId);
  }

  renderFilterComponent = () => {
    const { categoryId, options, type } = this.props;
    if (type === FilterType.INPUT_SELECT) {
      return (
        <InputFilter
          categoryId={ categoryId }
        />
      )
    }
    if (type === FilterType.CHECKBOX_SELECT) {
      return (
        <CheckBoxFilter
          categoryId={ categoryId }
          checkboxProperties={ options }
        />
      )
    }
  }

  render = () => {
    const { categoryId, hasValue, helpText, title } = this.props;
    return (
      <div className="search-filter-section">
        <div className="search-filter-section-header">
          <div className="search-filter-section-title">
            <div className="title-2">{ title }</div>
            {
              helpText &&
              <InfoButton
                infoText={ helpText }
                placement="top"
                size="small"
              />
            }
          </div>
          {
            hasValue &&
            <a onClick={ this.onClearFilter } className='btn btn-flat-icon'>
              <img className='icon icon-left'/>
              <span>{ CLEAR_BTN_TEXT }</span>
            </a>
          }
        </div>
        { this.renderFilterComponent() }
      </div>
    );
  }
};

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const filterValue = filterState[state.search.resource] ? filterState[state.search.resource][ownProps.categoryId] : null;
  let hasValue = false;
  if (filterValue && ownProps.type === FilterType.CHECKBOX_SELECT) {
    Object.keys(filterValue).forEach(key => {
      if (filterValue[key] === true) { hasValue = true; }
    })
  } else if (ownProps.type === FilterType.INPUT_SELECT) {
    hasValue = !!filterValue;
  }

  return {
    hasValue,
  }
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({
    clearFilter: (categoryId: string) => updateFilterByCategory({ categoryId, value: undefined }),
  }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps, OwnProps>(mapStateToProps, mapDispatchToProps)(FilterSection);
