// import { expectSaga, testSaga } from 'redux-saga-test-plan';
// import * as matchers from 'redux-saga-test-plan/matchers';
// import { throwError } from 'redux-saga-test-plan/providers';
//
// import { ResourceType, Badge, UpdateMethod, UpdateBadgeData } from 'interfaces';
// import globalState from 'fixtures/globalState';
// import {
//   getTableData,
//   getTableDataFailure,
//   getTableDataSuccess,
// } from 'ducks/tableMetadata/reducer';
// import * as API from '../api/v0';
// import reducer, {
//   getAllBadges,
//   getAllBadgesFailure,
//   getAllBadgesSuccess,
//   initialState,
//   BadgesReducerState,
//   updateBadges,
//   updateBadgesFailure,
//   updateBadgesSuccess,
// } from '../reducer';
//
// import {
//   getAllBadgesWatcher,
//   getAllBadgesWorker,
//   updateResourceBadgesWatcher,
//   updateResourceBadgesWorker,
// } from '../sagas';
// import { GetAllBadges, UpdateBadges } from '../types';
//
// describe('allBadges ducks', () => {
//   describe('actions', () => {
//     it('getAllBadges - returns the action to get all badges', () => {
//       const action = getAllBadges();
//       expect(action.type).toEqual(GetAllBadges.REQUEST);
//     });
//
//     it('getAllBadgesFailure - returns the action to process failure', () => {
//       const action = getAllBadgesFailure();
//       const { payload } = action;
//       expect(action.type).toBe(GetAllBadges.FAILURE);
//       expect(payload.allBadges).toEqual([]);
//     });
//
//     it('getAllBadgesSuccess - returns the action to process success', () => {
//       const expectedBadges = [
//         { badge_count: 2, badge_name: 'test' },
//         { badge_count: 1, badge_name: 'test2' },
//       ];
//       const action = getAllBadgesSuccess(expectedBadges);
//       const { payload } = action;
//       expect(action.type).toBe(GetAllBadges.SUCCESS);
//       expect(payload.allBadges).toBe(expectedBadges);
//     });
//   });
//
//   describe('reducer', () => {
//     let testState: BadgesReducerState;
//     beforeAll(() => {
//       testState = {
//         allBadges: {
//           isLoading: true,
//           badges: [],
//         },
//         resourceBadges: {
//           isLoading: false,
//           badges: [],
//         },
//       };
//     });
//     it('should return the existing state if action is not handled', () => {
//       expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
//     });
//
//     it('should handle GetAllBadges.REQUEST', () => {
//       expect(reducer(testState, getAllBadges())).toEqual({
//         allBadges: {
//           isLoading: true,
//           badges: [],
//         },
//         resourceBadges: {
//           isLoading: false,
//           badges: [],
//         },
//       });
//     });
//
//     it('should handle GetAllBadges.SUCCESS', () => {
//       const expectedBadges = [
//         { badge_count: 2, badge_name: 'test' },
//         { badge_count: 1, badge_name: 'test2' },
//       ];
//       expect(reducer(testState, getAllBadgesSuccess(expectedBadges))).toEqual({
//         allBadges: {
//           isLoading: false,
//           badges: expectedBadges,
//         },
//         resourceBadges: {
//           isLoading: false,
//           badges: [],
//         },
//       });
//     });
//
//     it('should return the initialState if GetAllBadges.FAILURE', () => {
//       expect(reducer(testState, getAllBadgesFailure())).toEqual(initialState);
//     });
//   });
//
//   describe('sagas', () => {
//     describe('getAllBadgesWatcher', () => {
//       it('takes GetAllBadges.REQUEST with getAllBadgesWorker', () => {
//         testSaga(getAllBadgesWatcher)
//           .next()
//           .takeEvery(GetAllBadges.REQUEST, getAllBadgesWorker)
//           .next()
//           .isDone();
//       });
//     });
//
//     describe('getAllBadgesWorker', () => {
//       it('gets allBadges', () => {
//         const mockBadges = [
//           { badge_count: 2, badge_name: 'test' },
//           { badge_count: 1, badge_name: 'test2' },
//         ];
//         return expectSaga(getAllBadgesWorker)
//           .provide([[matchers.call.fn(API.getAllBadges), mockBadges]])
//           .put(getAllBadgesSuccess(mockBadges))
//           .run();
//       });
//
//       it('handles request error', () =>
//         expectSaga(getAllBadgesWorker)
//           .provide([
//             [matchers.call.fn(API.getAllBadges), throwError(new Error())],
//           ])
//           .put(getAllBadgesFailure())
//           .run());
//     });
//   });
// });
//
// describe('badges ducks', () => {
//   let expectedBadges: Badge[];
//   let updatePayload: UpdateBadgeData[];
//   beforeAll(() => {
//     expectedBadges = [
//       { badge_count: 2, badge_name: 'test' },
//       { badge_count: 1, badge_name: 'test2' },
//     ];
//     updatePayload = [{ methodName: UpdateMethod.PUT, badgeName: 'test' }];
//   });
//
//   describe('actions', () => {
//     it('updateBadges - returns the action to updateBadges', () => {
//       const action = updateBadges(updatePayload, ResourceType.table, 'test');
//       const { payload } = action;
//       expect(action.type).toBe(UpdateBadges.REQUEST);
//       expect(payload.badgeArray).toBe(updatePayload);
//     });
//
//     it('updateBadgesFailure - returns the action to process failure', () => {
//       const action = updateBadgesFailure();
//       const { payload } = action;
//       expect(action.type).toBe(UpdateBadges.FAILURE);
//       expect(payload.badges).toEqual([]);
//     });
//
//     it('updateBadgesSuccess - returns the action to process success', () => {
//       const action = updateBadgesSuccess(expectedBadges);
//       const { payload } = action;
//       expect(action.type).toBe(UpdateBadges.SUCCESS);
//       expect(payload.badges).toBe(expectedBadges);
//     });
//   });
//
//   describe('reducer', () => {
//     let testState: BadgesReducerState;
//     beforeAll(() => {
//       testState = initialState;
//     });
//     it('should return the existing state if action is not handled', () => {
//       expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
//     });
//
//     it('should handle UpdateBadges.REQUEST', () => {
//       expect(
//         reducer(
//           testState,
//           updateBadges(updatePayload, ResourceType.table, 'test')
//         )
//       ).toEqual({
//         ...testState,
//         resourceBadges: {
//           ...testState.resourceBadges,
//           isLoading: true,
//         },
//       });
//     });
//
//     it('should handle UpdateBadges.FAILURE', () => {
//       expect(reducer(testState, updateBadgesFailure())).toEqual({
//         ...testState,
//         resourceBadges: {
//           ...testState.resourceBadges,
//           isLoading: false,
//         },
//       });
//     });
//
//     it('should handle UpdateBadges.SUCCESS', () => {
//       expect(reducer(testState, updateBadgesSuccess(expectedBadges))).toEqual({
//         ...testState,
//         resourceBadges: {
//           ...testState.resourceBadges,
//           isLoading: false,
//           badges: expectedBadges,
//         },
//       });
//     });
//
//     it('should handle GetTableData.REQUEST', () => {
//       expect(reducer(testState, getTableData('testKey'))).toEqual({
//         ...testState,
//         resourceBadges: {
//           ...testState.resourceBadges,
//           badges: [],
//           isLoading: true,
//         },
//       });
//     });
//
//     it('should handle GetTableData.FAILURE', () => {
//       const action = getTableDataFailure();
//       expect(reducer(testState, action)).toEqual({
//         ...testState,
//         resourceBadges: {
//           ...testState.resourceBadges,
//           badges: action.payload.badges,
//           isLoading: false,
//         },
//       });
//     });
//
//     it('should handle GetTableData.SUCCESS', () => {
//       const mockTableData = globalState.tableMetadata.tableData;
//       expect(
//         reducer(
//           testState,
//           getTableDataSuccess(mockTableData, {}, 200, expectedBadges)
//         )
//       ).toEqual({
//         ...testState,
//         resourceBadges: {
//           ...testState.resourceBadges,
//           badges: expectedBadges,
//           isLoading: false,
//         },
//       });
//     });
//   });
//
//   describe('sagas', () => {
//     describe('updateResourceBadgesWatcher', () => {
//       it('takes every UpdateBadges.REQUEST with updateResourceBadgesWorker', () => {
//         testSaga(updateResourceBadgesWatcher)
//           .next()
//           .takeEvery(UpdateBadges.REQUEST, updateResourceBadgesWorker);
//       });
//     });
//
//     describe('updateResourceBadgesWorker', () => {
//       /** TODO - fix syntax for testing `all` effect
//       it('executes flow for updating badges and returning up to date badge array', () => {
//         testSaga(updateResourceBadgesWorker, updateBadges(updatePayload, ResourceType.table, "test"))
//           .next().all(matchers.call.fn(API.updateResourceBadge), updatePayload, ResourceType.table, "test"))
//           .next().call(API.getResourceBadges, ResourceType.table, "test")
//           .next(expectedBadges).put(updateBadgesSuccess(expectedBadges))
//           .next().isDone();
//       });
//        */
//
//       it('handles request error', () => {
//         testSaga(
//           updateResourceBadgesWorker,
//           updateBadges(updatePayload, ResourceType.table, 'test')
//         )
//           .next(globalState)
//           .throw(new Error())
//           .put(updateBadgesFailure())
//           .next()
//           .isDone();
//       });
//     });
//   });
// });
