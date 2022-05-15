// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { ResourceType, TableResource } from 'interfaces';

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

const formatHighlightedDescription = (
    originalDescription: string,
    highlightedDescription: string[],
    ): string => {
        const highlightStart = highlightedDescription[0].replace('<em>', '').replace('</em>', '');
        console.log(highlightStart);
        const joinedSnippets = highlightedDescription.join('...');
        return originalDescription.startsWith(highlightStart)? joinedSnippets : ('...' + joinedSnippets);
    }

export const getHighlightedTableMetadata = (table: TableResource): HighlightedTable => {
    const highlightedTableResource: HighlightedTable = {
        name: table.name,
        description: '',
    }
    if (table.highlight) {
        console.log(table.highlight);
        // determine description formatting
        if (table.highlight.description) {
            // if there is a name match highlight just show the description as it is
            highlightedTableResource.description = table.highlight.name? table.description : formatHighlightedDescription(table.description, table.highlight.description);
        }
        else {
            highlightedTableResource.description = table.description;
        }

        // determine if matching column descriptions should be shown columns don't match
        if (table.highlight.columnDescriptions && !table.highlight.columns) {
            // show the first column description that matched
            highlightedTableResource.columnDescriptions = table.highlight.columnDescriptions[0];
        }

        if (table.highlight.columns) {
            highlightedTableResource.columns = table.highlight.columns.join(', ');
        }
    }
    else {
        highlightedTableResource.description = table.description;
    }
    return highlightedTableResource;
}