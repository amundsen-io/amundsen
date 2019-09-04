import { GlobalState } from 'ducks/rootReducer';
import { SearchReducerState } from 'ducks/search/reducer';
import { ResourceType } from 'interfaces/Resources';

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
