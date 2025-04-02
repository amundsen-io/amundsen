import { dashboardMetadata } from 'fixtures/metadata/dashboard';
import reducer, {
  getDashboard,
  getDashboardFailure,
  getDashboardSuccess,
  initialDashboardState,
  DashboardReducerState,
} from './reducer';

import { STATUS_CODES } from '../../constants';

describe('dashboard reducer', () => {
  let testState: DashboardReducerState;

  beforeAll(() => {
    testState = {
      isLoading: false,
      statusCode: STATUS_CODES.OK,
      dashboard: initialDashboardState,
    };
  });

  it('should return the existing state if action is not handled', () => {
    expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
  });

  it('should handle GetDashboard.REQUEST', () => {
    expect(reducer(testState, getDashboard({ uri: 'testUri' }))).toEqual({
      ...testState,
      isLoading: true,
      statusCode: null,
    });
  });

  it('should handle GetDashboard.SUCCESS', () => {
    expect(
      reducer(
        testState,
        getDashboardSuccess({
          dashboard: dashboardMetadata,
          statusCode: STATUS_CODES.ACCEPTED,
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: STATUS_CODES.ACCEPTED,
      dashboard: dashboardMetadata,
    });
  });

  it('should handle GetDashboard.FAILURE', () => {
    expect(
      reducer(
        testState,
        getDashboardFailure({
          statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: STATUS_CODES.INTERNAL_SERVER_ERROR,
      dashboard: initialDashboardState,
    });
  });
});
