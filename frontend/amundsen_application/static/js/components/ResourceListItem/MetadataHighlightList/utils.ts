// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import {
  DashboardResource,
  FeatureResource,
  TableResource,
  ResourceSearchHighlights,
} from 'interfaces';

/**
 * This file contains functions that control how diferrent resources are
 * highlighted depending on what the metadata for a result looks like to
 * provide users with the most useful metadata for every result
 */

export interface HighlightedResource {
  name: string;
  description: string;
}

export interface HighlightedTable extends HighlightedResource {
  columns?: string;
  columnDescriptions?: string;
}

export interface HighlightedDashboard extends HighlightedResource {
  queryNames?: string;
  chartNames?: string;
}

export const getDescription = (
  highlights: ResourceSearchHighlights,
  originalDescription: string
) => {
  if (highlights.description) {
    return highlights.description;
  }
  return originalDescription;
};

export const getHighlightedDashboardMetadata = (
  dashboard: DashboardResource
): HighlightedDashboard => {
  let description;
  let chartNames;
  let queryNames;

  if (dashboard.highlight) {
    description = getDescription(dashboard.highlight, dashboard.description);
    if (dashboard.highlight.chart_names) {
      chartNames = dashboard.highlight.chart_names.join(', ');
    }
    if (!dashboard.highlight.chart_names && dashboard.highlight.query_names) {
      // only show matching query names if not charts matched
      queryNames = dashboard.highlight.query_names.join(', ');
    }
  } else {
    description = dashboard.description;
  }
  return {
    name: dashboard.name,
    description,
    chartNames,
    queryNames,
  };
};

export const getHighlightedTableMetadata = (
  table: TableResource
): HighlightedTable => {
  let description;
  let columns;
  let columnDescriptions;

  if (table.highlight) {
    description = getDescription(table.highlight, table.description);
    if (table.highlight.columns) {
      columns = table.highlight.columns.join(', ');
    }
    // matching column descriptions should be shown if no columns match
    if (table.highlight.column_descriptions && !table.highlight.columns) {
      // show the first column description that matched
      const [firstColDescription] = table.highlight.column_descriptions;
      columnDescriptions = '"...' + firstColDescription + '..."';
    }
  } else {
    description = table.description;
  }
  return {
    name: table.name,
    description,
    columns,
    columnDescriptions,
  };
};

export const getHighlightedFeatureMetadata = (
  feature: FeatureResource
): HighlightedResource => {
  let description;
  if (feature.highlight) {
    description = getDescription(feature.highlight, feature.description);
  } else {
    description = feature.description;
  }
  return {
    name: feature.name,
    description,
  };
};
