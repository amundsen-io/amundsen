// TODO - Import 'delay' from 'redux-saga/effects' if we upgrade to 1.0
import { delay, SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { feedbackSubmit } from './api/v0';

import { ResetFeedback, SubmitFeedback, SubmitFeedbackRequest } from './types';

function* submitFeedbackWorker(action: SubmitFeedbackRequest): SagaIterator {
  try {
    yield call(feedbackSubmit, action.payload.data);
    yield put({ type: SubmitFeedback.SUCCESS });

    // TODO - yield delay(2000) on redux-saga upgrade
    yield call(delay, 2000);
    yield put({ type: ResetFeedback.REQUEST });
  } catch(error) {
    yield put({ type: SubmitFeedback.FAILURE });

    // TODO - yield delay(2000) on redux-saga upgrade
    yield call(delay, 2000);
    yield put({ type: ResetFeedback.REQUEST });
  }
}

export function* submitFeedbackWatcher(): SagaIterator {
  yield takeEvery(SubmitFeedback.REQUEST, submitFeedbackWorker);
}
