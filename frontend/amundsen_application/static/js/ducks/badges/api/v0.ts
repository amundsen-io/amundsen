// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import axios, { AxiosResponse } from 'axios';

import { Badge } from 'interfaces';

import { sortBadgesAlphabetical } from 'ducks/utilMethods';

export type AllBadgesAPI = {
  msg: string;
  badges: Badge[];
};

export function getAllBadges() {
  return axios
    .get('/api/metadata/v0/badges')
    .then((response: AxiosResponse<AllBadgesAPI>) =>
      response.data.badges.sort(sortBadgesAlphabetical)
    );
}
