import { combineReducers } from 'redux';

import dashboard, { DashboardReducerState } from 'ducks/dashboard/reducer';
import announcements, { AnnouncementsReducerState } from './announcements';
import feedback, { FeedbackReducerState } from './feedback/reducer';
import popularTables, {
  PopularTablesReducerState,
} from './popularTables/reducer';
import search, { SearchReducerState } from './search/reducer';
import tableMetadata, {
  TableMetadataReducerState,
} from './tableMetadata/reducer';
import lastIndexed, { LastIndexedReducerState } from './lastIndexed/reducer';
import tags, { TagsReducerState } from './tags/reducer';
import user, { UserReducerState } from './user/reducer';
import bookmarks, { BookmarkReducerState } from './bookmark/reducer';
import notification, { NotificationReducerState } from './notification/reducer';
import issue, { IssueReducerState } from './issue/reducer';

export interface GlobalState {
  announcements: AnnouncementsReducerState;
  bookmarks: BookmarkReducerState;
  dashboard: DashboardReducerState;
  feedback: FeedbackReducerState;
  issue: IssueReducerState;
  notification: NotificationReducerState;
  popularTables: PopularTablesReducerState;
  search: SearchReducerState;
  tableMetadata: TableMetadataReducerState;
  lastIndexed: LastIndexedReducerState;
  tags: TagsReducerState;
  user: UserReducerState;
}

export default combineReducers<GlobalState>({
  announcements,
  bookmarks,
  dashboard,
  feedback,
  issue,
  notification,
  popularTables,
  search,
  tableMetadata,
  lastIndexed,
  tags,
  user,
});
