import * as React from 'react';

import AppConfig from 'config/config';
import { logClick } from 'ducks/utilMethods';
import { TableMetadata } from 'interfaces';

export interface ExploreButtonProps {
  tableData: TableMetadata;
}

export class ExploreButton extends React.Component<ExploreButtonProps> {
  constructor(props) {
    super(props);
  }

  generateUrl() {
    const tableData = this.props.tableData;
    const partition = tableData.partition;

    if (partition.is_partitioned) {
      return AppConfig.tableProfile.exploreUrlGenerator(
        tableData.database, tableData.cluster, tableData.schema, tableData.name, partition.key, partition.value);
    }
    return AppConfig.tableProfile.exploreUrlGenerator(
      tableData.database, tableData.cluster, tableData.schema, tableData.name);
  }

  render() {
    if (!AppConfig.tableProfile.isExploreEnabled) {
      return null;
    }

    return (
      <a
        className="btn btn-default btn-lg"
        href={ this.generateUrl() }
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
