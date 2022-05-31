// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import {
  updateFilterByCategory,
  UpdateFilterRequest,
} from 'ducks/search/filters/reducer';

import InfoButton from 'components/InfoButton';

import ToggleSwitch from 'components/ToggleSwitch/ToggleSwitch';

import './styles.scss';

interface OwnProps {
  categoryId: string;
  filterName: string;
  helpText?: string;
}

interface StateFromProps {
  checked: boolean;
}

interface DispatchFromProps {
  applyFilters: (categoryId: string, value: string[]) => UpdateFilterRequest;
}
// TODO change to FC

export type ToggleFilterProps = OwnProps & DispatchFromProps & StateFromProps;

export class ToggleFilter extends React.Component<ToggleFilterProps> {
  handleChange = (checked) => {
    const { categoryId, applyFilters } = this.props;
    applyFilters(categoryId, [checked.toString()]);
  };

  render = () => {
    const { helpText, filterName, checked } = this.props;
    return (
      <label className="toggle-filter">
        <span className="search-filter-section-label">{filterName}</span>
        {helpText ? <InfoButton infoText={helpText} /> : null}
        <ToggleSwitch checked={checked} onChange={this.handleChange} />
      </label>
    );
  };
}

export const mapStateToProps = (state: GlobalState, ownProps: OwnProps) => {
  const filterState = state.search.filters;
  const filterValues = filterState[state.search.resource]
    ? filterState[state.search.resource][ownProps.categoryId]
    : undefined;
  const checked = filterValues ? filterValues.value === 'true' : false;
  return { checked };
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      applyFilters: (categoryId: string, value: string[]) =>
        updateFilterByCategory({
          searchFilters: [{ categoryId, value: value || undefined }],
        }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps, OwnProps>(
  mapStateToProps,
  mapDispatchToProps
)(ToggleFilter);
