import * as qs from 'simple-query-string';
import { createBrowserHistory } from 'history';

// https://github.com/ReactTraining/react-router/issues/3972#issuecomment-264805667
export const BrowserHistory = createBrowserHistory();

interface SearchParams {
  term?: string;
  resource?: string;
  index?: number;
}

export const updateSearchUrl = (searchParams: SearchParams, replace: boolean = false) => {
  // Explicitly listing out parameters to ensure consistent URL format
  const urlParams = qs.stringify({
    term: searchParams.term,
    resource: searchParams.resource,
    index: searchParams.index,
  });
  if (replace) {
    BrowserHistory.replace(`/search?${urlParams}`);
  } else {
    BrowserHistory.push(`/search?${urlParams}`);
  }
};
