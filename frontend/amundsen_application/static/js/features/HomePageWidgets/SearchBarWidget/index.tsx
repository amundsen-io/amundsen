// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import SearchBar, { SearchBarProps } from 'features/SearchBar'
import Breadcrumb from 'features/Breadcrumb';
import { SEARCH_BREADCRUMB_TEXT } from 'pages/HomePage/constants';

type SearchBarWidgetProps = SearchBarProps;

class SearchBarWidget extends React.Component<SearchBarWidgetProps> {
    render() {
        return(
            <div>
                <SearchBar />
                <div className="filter-breadcrumb pull-right">
                    <Breadcrumb
                        direction="right"
                        path="/search"
                        text={SEARCH_BREADCRUMB_TEXT}
                    />
                </div>
            </div>
        );
    }
}

export default SearchBarWidget 
