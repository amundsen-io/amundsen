import { GlobalState } from 'ducks/rootReducer';
import { SearchReducerState } from 'ducks/search/reducer';
import { DEFAULT_RESOURCE_TYPE, ResourceType } from 'interfaces/Resources';

export const getSearchState = (state: GlobalState): SearchReducerState => state.search;

export const getPageIndex = (state: SearchReducerState, resource?: ResourceType) => {
  resource = resource || state.selectedTab;
  switch(resource) {
    case ResourceType.table:
      return state.tables.page_index;
    case ResourceType.user:
      return state.users.page_index;
    case ResourceType.dashboard:
      return state.dashboards.page_index;
  };
  return 0;
};

export const autoSelectResource = (state: SearchReducerState) => {
  if (state.tables && state.tables.total_results > 0) {
    return ResourceType.table;
  }
  if (state.users && state.users.total_results > 0) {
    return ResourceType.user
  }
  if (state.dashboards && state.dashboards.total_results > 0) {
    return ResourceType.dashboard
  }
  return DEFAULT_RESOURCE_TYPE;
};
