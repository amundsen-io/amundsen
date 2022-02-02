import {
  LoggedInUser,
  PeopleUser,
  Resource,
  ResourceType,
  ResourceDict,
} from 'interfaces';

import {
  CreateUser,
  CreateUserRequest,
  CreateUserResponse,
  ActivateUser,
  ActivateUserRequest,
  ActivateUserResponse,
  GetLoggedInUser,
  GetLoggedInUserRequest,
  GetLoggedInUserResponse,
  GetUser,
  GetUserRequest,
  GetUserResponse,
  GetUserOwn,
  GetUserOwnRequest,
  GetUserOwnResponse,
  GetUserRead,
  GetUserReadRequest,
  GetUserReadResponse,
} from './types';

/* ACTIONS */
export function getLoggedInUser(): GetLoggedInUserRequest {
  return { type: GetLoggedInUser.REQUEST };
}
export function getLoggedInUserFailure(): GetLoggedInUserResponse {
  return { type: GetLoggedInUser.FAILURE };
}
export function getLoggedInUserSuccess(
  user: LoggedInUser
): GetLoggedInUserResponse {
  return { type: GetLoggedInUser.SUCCESS, payload: { user } };
}

export function createUser(user: any): CreateUserRequest {
  return { type: CreateUser.REQUEST, payload: { user } };
}
export function createUserFailure(): CreateUserResponse {
  return { type: CreateUser.FAILURE };
}
export function createUserSuccess(user: LoggedInUser): CreateUserResponse {
  return { type: CreateUser.SUCCESS, payload: { user } };
}

export function activateUser(databricksId: string): ActivateUserRequest {
  return { type: ActivateUser.REQUEST, payload: { databricksId } };
}
export function activateUserFailure(): ActivateUserResponse {
  return { type: ActivateUser.FAILURE };
}
export function activateUserSuccess(user: PeopleUser): ActivateUserResponse {
  return { type: ActivateUser.SUCCESS };
}

export function getUser(
  userId: string,
  index?: string,
  source?: string
): GetUserRequest {
  return { type: GetUser.REQUEST, payload: { userId, index, source } };
}
export function getUserFailure(): GetUserResponse {
  return { type: GetUser.FAILURE };
}
export function getUserSuccess(user: PeopleUser): GetUserResponse {
  return { type: GetUser.SUCCESS, payload: { user } };
}

export function getUserOwn(userId: string): GetUserOwnRequest {
  return { type: GetUserOwn.REQUEST, payload: { userId } };
}
export function getUserOwnFailure(): GetUserOwnResponse {
  return { type: GetUserOwn.FAILURE };
}
export function getUserOwnSuccess(
  own: ResourceDict<Resource[]>
): GetUserOwnResponse {
  return { type: GetUserOwn.SUCCESS, payload: { own } };
}

export function getUserRead(userId: string): GetUserReadRequest {
  return { type: GetUserRead.REQUEST, payload: { userId } };
}
export function getUserReadFailure(): GetUserReadResponse {
  return { type: GetUserRead.FAILURE };
}
export function getUserReadSuccess(read: Resource[]): GetUserReadResponse {
  return { type: GetUserRead.SUCCESS, payload: { read } };
}

/* REDUCER */
export interface UserReducerState {
  loggedInUser: LoggedInUser;
  profile: {
    own: ResourceDict<Resource[]>;
    read: Resource[];
    user: PeopleUser;
  };
}

export const defaultUser = {
  display_name: '',
  email: '',
  employee_type: '',
  first_name: '',
  full_name: '',
  github_username: '',
  is_active: true,
  last_name: '',
  manager_fullname: '',
  profile_url: '',
  role_name: '',
  slack_id: '',
  team_name: '',
  user_id: '',
};
export const initialOwnState = {
  [ResourceType.table]: [],
  [ResourceType.dashboard]: [],
};
export const initialState: UserReducerState = {
  loggedInUser: defaultUser,
  profile: {
    own: initialOwnState,
    read: [],
    user: defaultUser,
  },
};

export default function reducer(
  state: UserReducerState = initialState,
  action
): UserReducerState {
  switch (action.type) {
    case GetLoggedInUser.SUCCESS: {
      const { payload } = <GetLoggedInUserResponse>action;
      if (payload === undefined) {
        throw Error('payload must be set for GetLoggedInUser.SUCCESS');
      }
      return {
        ...state,
        loggedInUser: payload.user,
      };
    }
    case CreateUser.REQUEST:
    case CreateUser.FAILURE:
      return {
        ...state,
        profile: {
          ...state.profile,
          user: defaultUser,
        },
      };
    case CreateUser.SUCCESS:
      const { payload } = <CreateUserResponse>action;
      if (payload === undefined) {
        throw Error('payload must be set for CreateUserResponse.SUCCESS');
      }
      return {
        ...state,
        loggedInUser: payload.user,
        profile: {
          ...state.profile,
          user: payload.user,
        },
      };
    case GetUser.REQUEST:
    case GetUser.FAILURE:
      return {
        ...state,
        profile: {
          ...state.profile,
          user: defaultUser,
        },
      };
    case GetUser.SUCCESS: {
      const { payload } = <GetUserResponse>action;
      if (payload === undefined) {
        throw Error('payload must be set for GetUser.SUCCESS');
      }
      return {
        ...state,
        profile: {
          ...state.profile,
          user: payload.user,
        },
      };
    }
    case GetUserOwn.REQUEST:
    case GetUserOwn.FAILURE:
      return {
        ...state,
        profile: {
          ...state.profile,
          own: {
            ...initialOwnState,
          },
        },
      };
    case GetUserOwn.SUCCESS: {
      const { payload } = <GetUserOwnResponse>action;
      if (payload === undefined) {
        throw Error('payload must be set for GetUserOwn.SUCCESS');
      }
      return {
        ...state,
        profile: {
          ...state.profile,
          own: payload.own,
        },
      };
    }
    case GetUserRead.REQUEST:
    case GetUserRead.FAILURE:
      return {
        ...state,
        profile: {
          ...state.profile,
          read: [],
        },
      };
    case GetUserRead.SUCCESS: {
      const { payload } = <GetUserReadResponse>action;
      if (payload === undefined) {
        throw Error('payload must be set for GetUserRead.SUCCESS');
      }
      return {
        ...state,
        profile: {
          ...state.profile,
          read: payload.read,
        },
      };
    }
    default:
      return state;
  }
}
