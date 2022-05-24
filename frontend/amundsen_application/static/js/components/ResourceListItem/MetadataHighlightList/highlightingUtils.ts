// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { DashboardResource, TableResource } from 'interfaces';

/**
 * This file contains functions that control how diferrent resources are
 * highlighted depending on what the metadata for a result looks like to
 * provide users with the most useful metadata for every result
 */

export interface HighlightedTable {
  name: string;
  description: string;
  columns?: string;
  columnDescriptions?: string;
}
export interface HighlightedDashboard {
  name: string;
  description: string;
  queryNames?: string;
  chartNames?: string;
}

const formatHighlightedDescription = (
  originalDescription: string,
  highlightedDescription: string[]
): string => {
  const highlightStart = highlightedDescription[0]
    .replace('<em>', '')
    .replace('</em>', '');
  const joinedSnippets = highlightedDescription.join('...');
  const newDescription = originalDescription.startsWith(highlightStart)
    ? joinedSnippets
    : '...' + joinedSnippets;

  if (
    highlightedDescription.length === 1 &&
    !originalDescription.startsWith(highlightStart)
  ) {
    // if we only have one snippet and its not at the start add the rest of the description for context
    const highlightFinishIndex =
      originalDescription.indexOf(highlightStart) + highlightStart.length;
    return newDescription + originalDescription.substring(highlightFinishIndex);
  }
  return newDescription;
};

export const getHighlightedDashboardMetadata = (
  dashboard: DashboardResource
): HighlightedDashboard => {
  const highlightedDashboardResource: HighlightedDashboard = {
    name: dashboard.name,
    description: '',
  };
  if (dashboard.highlight) {
    // determine description formatting
    if (dashboard.highlight.description) {
      // if there is a name match highlight just show the description as it is
      highlightedDashboardResource.description = dashboard.highlight.name
        ? dashboard.description
        : formatHighlightedDescription(
            dashboard.description,
            dashboard.highlight.description
          );
    } else {
      highlightedDashboardResource.description = dashboard.description;
    }
    if (dashboard.highlight.chart_names) {
      highlightedDashboardResource.chartNames = dashboard.highlight.chart_names.join(
        ', '
      );
    }
    if (!dashboard.highlight.chart_names && dashboard.highlight.query_names) {
      // only show matching query names if not charts matched
      highlightedDashboardResource.queryNames = dashboard.highlight.query_names.join(
        ', '
      );
    }
  } else {
    highlightedDashboardResource.description = dashboard.description;
  }
  return highlightedDashboardResource;
};

export const getHighlightedTableMetadata = (
  table: TableResource
): HighlightedTable => {
  const highlightedTableResource: HighlightedTable = {
    name: table.name,
    description: '',
  };
  if (table.highlight) {
    // determine description formatting
    if (table.highlight.description) {
      // if there is a name match highlight just show the description as it is
      highlightedTableResource.description = table.highlight.name
        ? table.description
        : formatHighlightedDescription(
            table.description,
            table.highlight.description
          );
    } else {
      highlightedTableResource.description = table.description;
    }

    // determine if matching column descriptions should be shown columns don't match
    if (table.highlight.columnDescriptions && !table.highlight.columns) {
      // show the first column description that matched
      const [firstColDescription] = table.highlight.columnDescriptions;
      highlightedTableResource.columnDescriptions = firstColDescription;
    }

    if (table.highlight.columns) {
      highlightedTableResource.columns = table.highlight.columns.join(', ');
    }
  } else {
    highlightedTableResource.description = table.description;
  }
  return highlightedTableResource;
};
