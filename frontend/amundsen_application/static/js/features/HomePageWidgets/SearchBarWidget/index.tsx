// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { withRouter } from 'react-router-dom';
import { connect } from 'react-redux';

import SearchBar, {
  SearchBarProps,
  StateFromProps,
  DispatchFromProps,
  OwnProps,
  mapStateToProps,
  mapDispatchToProps,
} from 'features/SearchBar';
import Breadcrumb from 'features/Breadcrumb';
import { SEARCH_BREADCRUMB_TEXT } from 'pages/HomePage/constants';

export type SearchBarWidgetProps = SearchBarProps;

export const SearchBarWidget: React.FC<SearchBarWidgetProps> = (
  props: SearchBarWidgetProps
) => (
  <div>
    {/* eslint-disable-next-line react/jsx-props-no-spreading*/}
    <SearchBar {...props} />
    <div className="filter-breadcrumb pull-right">
      <Breadcrumb
        direction="right"
        path="/search"
        text={SEARCH_BREADCRUMB_TEXT}
      />
    </div>
  </div>
);

export default withRouter(
  connect<StateFromProps, DispatchFromProps, OwnProps>(
    mapStateToProps,
    mapDispatchToProps
  )(SearchBarWidget)
);
