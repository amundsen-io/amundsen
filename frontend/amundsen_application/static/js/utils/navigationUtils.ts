import * as qs from 'simple-query-string';
import { createBrowserHistory } from 'history';

import { ResourceType } from 'interfaces/Resources';

// https://github.com/ReactTraining/react-router/issues/3972#issuecomment-264805667
export const BrowserHistory = createBrowserHistory();

export interface SearchParams {
  term?: string;
  resource?: ResourceType;
  index?: number;
  filters?: {};
}

export const DEFAULT_SEARCH_ROUTE = '/search';

export const generateSearchUrl = (searchParams: SearchParams): string => {
  const filtersForResource =
    (searchParams.filters && searchParams.filters[searchParams.resource]) || {};
  const hasFilters = Object.keys(filtersForResource).length > 0;

  // If there is no search input return the search route url
  if (!searchParams.term && !hasFilters) {
    return DEFAULT_SEARCH_ROUTE;
  }

  // Explicitly list out parameters to ensure consistent URL format
  const queryStringValues = {
    term: searchParams.term || undefined,
    resource: searchParams.resource,
    index: searchParams.index,
  };
  if (hasFilters) {
    // eslint-disable-next-line @typescript-eslint/dot-notation
    queryStringValues['filters'] = filtersForResource;
  }

  const urlParams = qs.stringify(queryStringValues);
  return `${DEFAULT_SEARCH_ROUTE}?${urlParams}`;
};

export const updateSearchUrl = (
  searchParams: SearchParams,
  replace: boolean = false
) => {
  const newUrl = generateSearchUrl(searchParams);

  if (replace) {
    BrowserHistory.replace(newUrl);
  } else {
    BrowserHistory.push(newUrl);
  }
};

/**
 * Creates the dashboard detail URL from the URI
 * @param URI String  URI of the dashboard, it has this shape: uri = "<product>_dashboard://<cluster>.<groupID>/<dashboardID>"
 * @return String     Dashboard Detail page URL
 */
export const buildDashboardURL = (URI: string) => {
  return `/dashboard/${encodeURIComponent(URI)}`;
};
