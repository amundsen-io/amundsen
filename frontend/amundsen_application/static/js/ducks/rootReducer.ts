import { combineReducers } from 'redux';

import announcements, { AnnouncementsReducerState } from './announcements/reducer';
import feedback, { FeedbackReducerState } from './feedback/reducer';
import popularTables, { PopularTablesReducerState } from './popularTables/reducer';
import search, { SearchReducerState } from './search/reducer';
import tableMetadata, { TableMetadataReducerState } from './tableMetadata/reducer';
import tags, { TagReducerState } from './tags/reducer';
import user, { UserReducerState } from './user/reducer';

export interface GlobalState {
  announcements: AnnouncementsReducerState;
  feedback: FeedbackReducerState;
  popularTables: PopularTablesReducerState;
  search: SearchReducerState;
  tableMetadata: TableMetadataReducerState;
  tags: TagReducerState;
  user: UserReducerState;
}

export default combineReducers<GlobalState>({
  announcements,
  feedback,
  popularTables,
  search,
  tableMetadata,
  tags,
  user,
});
