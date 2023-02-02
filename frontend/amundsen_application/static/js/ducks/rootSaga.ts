import { all } from 'redux-saga/effects';

import { getAllBadgesWatcher } from 'ducks/badges/sagas';
import {
  addBookmarkWatcher,
  getBookmarksForUserWatcher,
  getBookmarksWatcher,
  removeBookmarkWatcher,
} from 'ducks/bookmark/sagas';
import { getDashboardWatcher } from 'ducks/dashboard/sagas';
import {
  getFeatureCodeWatcher,
  getFeatureDescriptionWatcher,
  getFeatureLineageWatcher,
  getFeaturePreviewDataWatcher,
  getFeatureWatcher,
  updateFeatureDescriptionWatcher,
  updateFeatureOwnerWatcher,
} from 'ducks/feature/sagas';
import { getAnnouncementsWatcher } from './announcements/sagas';
import { submitNotificationWatcher } from './notification/sagas';
import { getNoticesWatcher } from './notices';
import { submitFeedbackWatcher } from './feedback/sagas';
import { createIssueWatcher, getIssuesWatcher } from './issue/sagas';
import { getPopularResourcesWatcher } from './popularResources/sagas';
import {
  inlineSearchWatcher,
  inlineSearchWatcherDebounce,
  loadPreviousSearchWatcher,
  searchAllWatcher,
  searchResourceWatcher,
  selectInlineResultsWatcher,
  submitSearchResourceWatcher,
  submitSearchWatcher,
  updateSearchStateWatcher,
  urlDidUpdateWatcher,
} from './search/sagas';
import { filterWatcher } from './search/filters/sagas';
import { updateTableOwnerWatcher } from './tableMetadata/owners/sagas';
import {
  getColumnDescriptionWatcher,
  getPreviewDataWatcher,
  getTableDataWatcher,
  getTableDescriptionWatcher,
  getTableQualityChecksWatcher,
  getTypeMetadataDescriptionWatcher,
  updateColumnDescriptionWatcher,
  updateTableDescriptionWatcher,
  updateTypeMetadataDescriptionWatcher,
} from './tableMetadata/sagas';
import { getLastIndexedWatcher } from './lastIndexed/sagas';
import { getAllTagsWatcher, updateResourceTagsWatcher } from './tags/sagas';
import {
  getLoggedInUserWatcher,
  getUserOwnWatcher,
  getUserReadWatcher,
  getUserWatcher,
} from './user/sagas';
import {
  getColumnLineageWatcher,
  getTableColumnLineageWatcher,
  getTableLineageWatcher,
} from './lineage/sagas';

export default function* rootSaga() {
  yield all([
    addBookmarkWatcher(),
    createIssueWatcher(),
    filterWatcher(),
    getAllBadgesWatcher(),
    getAllTagsWatcher(),
    getAnnouncementsWatcher(),
    getBookmarksForUserWatcher(),
    getBookmarksWatcher(),
    getColumnDescriptionWatcher(),
    getColumnLineageWatcher(),
    getDashboardWatcher(),
    getFeatureCodeWatcher(),
    getFeatureDescriptionWatcher(),
    getFeatureLineageWatcher(),
    getFeaturePreviewDataWatcher(),
    getFeatureWatcher(),
    getIssuesWatcher(),
    getLastIndexedWatcher(),
    getLoggedInUserWatcher(),
    getNoticesWatcher(),
    getPopularResourcesWatcher(),
    getPreviewDataWatcher(),
    getTableColumnLineageWatcher(),
    getTableDataWatcher(),
    getTableDescriptionWatcher(),
    getTableLineageWatcher(),
    getTableQualityChecksWatcher(),
    getTypeMetadataDescriptionWatcher(),
    getUserOwnWatcher(),
    getUserReadWatcher(),
    getUserWatcher(),
    inlineSearchWatcher(),
    inlineSearchWatcherDebounce(),
    loadPreviousSearchWatcher(),
    removeBookmarkWatcher(),
    searchAllWatcher(),
    searchResourceWatcher(),
    selectInlineResultsWatcher(),
    submitFeedbackWatcher(),
    submitNotificationWatcher(),
    submitSearchResourceWatcher(),
    submitSearchWatcher(),
    updateColumnDescriptionWatcher(),
    updateFeatureDescriptionWatcher(),
    updateFeatureOwnerWatcher(),
    updateResourceTagsWatcher(),
    updateSearchStateWatcher(),
    updateTableDescriptionWatcher(),
    updateTableOwnerWatcher(),
    updateTypeMetadataDescriptionWatcher(),
    urlDidUpdateWatcher(),
  ]);
}
