import { AnnouncementPost } from 'interfaces';

import { GetAnnouncements, GetAnnouncementsRequest, GetAnnouncementsResponse } from './types';

/* ACTIONS */
export function getAnnouncements(): GetAnnouncementsRequest {
  return { type: GetAnnouncements.REQUEST };
};

/* REDUCER */
export interface AnnouncementsReducerState {
  posts: AnnouncementPost[];
};

export const initialState: AnnouncementsReducerState = {
  posts: [],
};

export default function reducer(state: AnnouncementsReducerState = initialState, action): AnnouncementsReducerState {
  switch (action.type) {
    case GetAnnouncements.FAILURE:
      return initialState;
    case GetAnnouncements.SUCCESS:
      return { posts: (<GetAnnouncementsResponse>action).payload.posts };
    default:
      return state;
  }
};
