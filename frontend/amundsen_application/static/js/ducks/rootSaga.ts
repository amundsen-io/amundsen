import { all } from 'redux-saga/effects';

// AnnouncementPage
import { announcementsGetWatcher } from "./announcements/sagas";

// DataPreviewButton
import { getPreviewDataWatcher } from './preview/sagas';

// FeedbackForm
import { submitFeedbackWatcher } from './feedback/sagas';

// SearchPage
import { getPopularTablesWatcher } from './popularTables/sagas';
import { executeSearchWatcher } from './search/sagas';

// TableDetail
import {
  getTableDataWatcher,
  getColumnDescriptionWatcher,
  getLastIndexedWatcher,
  getTableDescriptionWatcher,
  updateColumnDescriptionWatcher,
  updateTableDescriptionWatcher,
  updateTableOwnerWatcher,
  updateTagsWatcher,
} from './tableMetadata/sagas';

// Tags
import { getAllTagsWatcher } from './tags/sagas';

// User
import { getCurrentUserWatcher } from "./user/sagas";

export default function* rootSaga() {
  yield all([
    // AnnouncementPage
    announcementsGetWatcher(),
    // DataPreviewButton
    getPreviewDataWatcher(),
    // FeedbackForm
    submitFeedbackWatcher(),
    // SearchPage
    executeSearchWatcher(),
    getPopularTablesWatcher(),
    // Tags
    getAllTagsWatcher(),
    updateTagsWatcher(),
    // TableDetail
    getTableDataWatcher(),
    getColumnDescriptionWatcher(),
    getLastIndexedWatcher(),
    getTableDescriptionWatcher(),
    updateColumnDescriptionWatcher(),
    updateTableDescriptionWatcher(),
    updateTableOwnerWatcher(),
    // User
    getCurrentUserWatcher(),
  ]);
}
