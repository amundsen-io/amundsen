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
  let finalDescription;
  let chartNames;
  let queryNames;
  const { name, description, highlight } = dashboard;

  if (highlight) {
    finalDescription = getDescription(highlight, description);
    if (highlight.chart_names) {
      chartNames = highlight.chart_names.join(', ');
    }
    if (!highlight.chart_names && highlight.query_names) {
      // only show matching query names if not charts matched
      queryNames = highlight.query_names.join(', ');
    }
  } else {
    finalDescription = description;
  }
  return {
    name,
    description: finalDescription,
    chartNames,
    queryNames,
  };
};

export const getHighlightedTableMetadata = (
  table: TableResource
): HighlightedTable => {
  let finalDescription;
  let columns;
  let columnDescriptions;
  const { name, description, highlight } = table;

  if (highlight) {
    finalDescription = getDescription(highlight, description);
    if (highlight.columns) {
      columns = highlight.columns.join(', ');
    }
    // matching column descriptions should be shown if no columns match
    if (highlight.column_descriptions && !highlight.columns) {
      // show the first column description that matched
      const [firstColDescription] = highlight.column_descriptions;
      columnDescriptions = '"...' + firstColDescription + '..."';
    }
  } else {
    finalDescription = description;
  }
  return {
    name,
    description: finalDescription,
    columns,
    columnDescriptions,
  };
};

export const getHighlightedFeatureMetadata = (
  feature: FeatureResource
): HighlightedResource => {
  let finalDescription;
  const { name, description, highlight } = feature;
  if (highlight) {
    finalDescription = getDescription(highlight, description);
  } else {
    finalDescription = description;
  }
  return {
    name,
    description: finalDescription,
  };
};
