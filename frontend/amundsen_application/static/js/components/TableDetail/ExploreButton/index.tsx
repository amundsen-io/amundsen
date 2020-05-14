import * as React from 'react';

import { logClick } from 'ducks/utilMethods';
import { TableMetadata } from 'interfaces';
import { exploreEnabled, generateExploreUrl } from 'config/config-utils';

export interface ExploreButtonProps {
  tableData: TableMetadata;
}

class ExploreButton extends React.Component<ExploreButtonProps> {
  render() {
    const url = generateExploreUrl(this.props.tableData);
    if (!url || !exploreEnabled()) {
      return null;
    }

    return (
      <a
        className="btn btn-default btn-lg"
        href={ url }
        role="button"
        target="_blank"
        id="explore-sql"
        onClick={ logClick }
      >
        Explore
      </a>
    );
  }
};

export default ExploreButton;
