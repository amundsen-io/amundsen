import { RouteComponentProps } from 'react-router';

import * as History from 'history';

// Mock React-Router
export function getMockRouterProps<P>(
  data: P,
  location: Partial<History.Location>
): RouteComponentProps<P> {
  const mockLocation: History.Location = {
    hash: '',
    key: '',
    pathname: '',
    search: '',
    state: {},
    ...location,
  };

  const props: RouteComponentProps<P> = {
    match: {
      isExact: true,
      params: data,
      path: '',
      url: '',
    },
    location: mockLocation,
    history: {
      length: 2,
      action: 'POP',
      location: mockLocation,
      push: null,
      replace: null,
      go: null,
      goBack: null,
      goForward: null,
      block: null,
      createHref: null,
      listen: null,
    },
    staticContext: {},
  };

  return props;
}
