import { all } from 'redux-saga/effects';

// AnnouncementPage
import { announcementsGetWatcher } from "./announcements/sagas";

// FeedbackForm
import { submitFeedbackWatcher } from './feedback/sagas';

// SearchPage
import { getPopularTablesWatcher } from './popularTables/sagas';
import { searchAllWatcher, searchResourceWatcher } from './search/sagas';

// TableDetail
import { updateTableOwnerWatcher } from './tableMetadata/owners/sagas';
import { updateTableTagsWatcher } from './tableMetadata/tags/sagas';
import {
  getTableDataWatcher,
  getColumnDescriptionWatcher,
  getLastIndexedWatcher,
  getPreviewDataWatcher,
  getTableDescriptionWatcher,
  updateColumnDescriptionWatcher,
  updateTableDescriptionWatcher,
} from './tableMetadata/sagas';

// Tags
import { getAllTagsWatcher } from './allTags/sagas';

// User
import { getLoggedInUserWatcher, getUserWatcher } from "./user/sagas";

export default function* rootSaga() {
  yield all([
    // AnnouncementPage
    announcementsGetWatcher(),
    // FeedbackForm
    submitFeedbackWatcher(),
    // SearchPage
    searchAllWatcher(),
    searchResourceWatcher(),
    getPopularTablesWatcher(),
    // Tags
    getAllTagsWatcher(),
    // TableDetail
    getTableDataWatcher(),
    getColumnDescriptionWatcher(),
    getLastIndexedWatcher(),
    getPreviewDataWatcher(),
    getTableDescriptionWatcher(),
    updateColumnDescriptionWatcher(),
    updateTableDescriptionWatcher(),
    updateTableOwnerWatcher(),
    updateTableTagsWatcher(),
    // User
    getLoggedInUserWatcher(),
    getUserWatcher(),
  ]);
}
