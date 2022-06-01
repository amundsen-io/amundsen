// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { DashboardResource, FeatureResource, TableResource } from 'interfaces';

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

export const formatHighlightedDescription = (
  originalDescription: string,
  highlightedDescription: string[]
): string => {
  originalDescription = originalDescription.replace(/(\r\n|\n|\r)/gm, "");
  highlightedDescription= highlightedDescription.filter((snippet) => snippet.replace(/(\r\n|\n|\r)/gm, ""));
  const highlightStart = highlightedDescription[0]
    .replace('<em>', '')
    .replace('</em>', '');
  const joinedSnippets = highlightedDescription.join('...');
  const newDescription = originalDescription.startsWith(highlightStart)
    ? joinedSnippets
    : '...' + joinedSnippets;

  if (highlightedDescription.length === 1) {
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
      highlightedDashboardResource.description = formatHighlightedDescription(
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
      highlightedTableResource.description = formatHighlightedDescription(
            table.description,
            table.highlight.description
          );
    } else {
      highlightedTableResource.description = table.description;
    }

    // determine if matching column descriptions should be shown columns don't match
    if (table.highlight.column_descriptions && !table.highlight.columns) {
      // show the first column description that matched
      const [firstColDescription] = table.highlight.column_descriptions;
      highlightedTableResource.columnDescriptions = '"...' + firstColDescription + '..."';
    }

    if (table.highlight.columns) {
      highlightedTableResource.columns = table.highlight.columns.join(', ');
    }
  } else {
    highlightedTableResource.description = table.description;
  }
  return highlightedTableResource;
};

export const getHighlightedFeatureMetadata = (
  feature: FeatureResource
): HighlightedResource => {
  const highlightedResource: HighlightedResource = {
    name: feature.name,
    description: '',
  };
  if (feature.highlight) {
    // determine description formatting
    if (feature.highlight.description) {
      // if there is a name match highlight just show the description as it is
      highlightedResource.description = formatHighlightedDescription(
            feature.description,
            feature.highlight.description
          );
    } else {
      highlightedResource.description = feature.description;
    }
  }
  return highlightedResource;
};
