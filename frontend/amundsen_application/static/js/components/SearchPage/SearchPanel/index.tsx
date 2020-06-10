import * as React from 'react';

import './styles.scss';

type SearchPanelProps = {
  children: React.ReactNode;
};

const SearchPanel: React.SFC = ({ children }: SearchPanelProps) => {
  return (
    <div className="search-control-panel">
      {React.Children.map(children, (child, index) => {
        return (
          <div key={`search-panel-child:${index}`} className="section">
            {child}
          </div>
        );
      })}
    </div>
  );
};

export default SearchPanel;
