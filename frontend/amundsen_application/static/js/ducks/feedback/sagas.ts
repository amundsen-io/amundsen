// TODO - Import 'delay' from 'redux-saga/effects' if we upgrade to 1.0
import { delay, SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import { ResetFeedback, SubmitFeedback, SubmitFeedbackRequest } from './reducer';
import { feedbackSubmitFeedback } from '../api/feedback/v0';


function* submitFeedbackWorker(action: SubmitFeedbackRequest): SagaIterator {
  try {
    yield call(feedbackSubmitFeedback, action);
    yield put({ type: SubmitFeedback.SUCCESS });

    // TODO - yield delay(2000) on redux-saga upgrade
    yield call(delay, 2000);
    yield put({ type: ResetFeedback.ACTION });
  } catch(error) {
    yield put({ type: SubmitFeedback.FAILURE });
  }
}

export function* submitFeedbackWatcher(): SagaIterator {
  yield takeEvery(SubmitFeedback.ACTION, submitFeedbackWorker);
}
