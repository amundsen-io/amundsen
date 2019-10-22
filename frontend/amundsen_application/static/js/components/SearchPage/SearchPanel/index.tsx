import * as React from 'react';

import './styles.scss';

const SearchPanel: React.SFC = ({ children }) => {
  return (
    <div className="search-control-panel">
      {
        React.Children.map(children, (child, index) => {
          return (
            <div key={`search-panel-child:${index}`} className="section">
              { child }
            </div>
          );
        })
      }
    </div>
  );
};

export default SearchPanel;
