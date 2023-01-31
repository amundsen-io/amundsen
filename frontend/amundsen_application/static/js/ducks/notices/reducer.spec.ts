import { aNoticeTestData } from 'fixtures/metadata/notices';
import {
  reducer,
  getNotices,
  getNoticesFailure,
  getNoticesSuccess,
  initialNoticesState,
  NoticesReducerState,
} from '.';

const testData = aNoticeTestData().withQualityIssue().build();

describe('notices reducer', () => {
  let testState: NoticesReducerState;

  beforeAll(() => {
    testState = {
      isLoading: false,
      statusCode: 200,
      notices: initialNoticesState,
    };
  });

  it('should return the existing state if action is not handled', () => {
    expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
  });

  it('should handle GetNotices.REQUEST', () => {
    expect(reducer(testState, getNotices('testKey'))).toEqual({
      ...testState,
      isLoading: true,
      statusCode: null,
    });
  });

  it('should handle GetNotices.SUCCESS', () => {
    expect(reducer(testState, getNoticesSuccess(testData, 202))).toEqual({
      isLoading: false,
      statusCode: 202,
      notices: testData,
    });
  });

  it('should handle GetNotices.FAILURE', () => {
    expect(reducer(testState, getNoticesFailure(500, 'oops'))).toEqual({
      isLoading: false,
      statusCode: 500,
      notices: initialNoticesState,
    });
  });
});
