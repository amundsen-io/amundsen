import { Resource, DashboardResource, TableResource, UserResource } from "../../components/common/ResourceListItem/types";

interface SearchResults<T extends Resource> {
  page_index: number;
  total_results: number;
  results: T[];
}

export type DashboardSearchResults = SearchResults<DashboardResource>;
export type TableSearchResults = SearchResults<TableResource>;
export type UserSearchResults = SearchResults<UserResource>;
