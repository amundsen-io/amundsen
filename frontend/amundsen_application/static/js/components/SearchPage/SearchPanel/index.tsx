// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import './styles.scss';

type SearchPanelProps = {
  children: React.ReactNode;
};

const SearchPanel: React.SFC = ({ children }: SearchPanelProps) => {
  return (
    <aside className="search-control-panel">
      {React.Children.map(children, (child, index) => {
        return (
          <div key={`search-panel-child:${index}`} className="section">
            {child}
          </div>
        );
      })}
    </aside>
  );
};

export default SearchPanel;
