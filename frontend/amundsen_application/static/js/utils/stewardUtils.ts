import {
  StewardDict,
  ResourceType,
  UpdateStewardPayload,
  User,
} from 'interfaces';
import { indexUsersEnabled } from 'config/config-utils';
import { StewardItemProps } from 'components/StewardEditor';
import * as API from 'ducks/tableMetadata/api/v0';

/**
 * Converts a list of Users to a dictionary of users StewardsDict
 */
export function getStewardsDictFromUsers(stewards: User[]): StewardDict {
  const stewardObj = stewards.reduce((resultObj, currentSteward) => {
    resultObj[currentSteward.user_id] = currentSteward as User;
    return resultObj;
  }, {});
  return stewardObj;
}

/**
 * Converts a list of Users to StewardItemProps
 */
export function getStewardItemPropsFromUsers(
  stewards: User[],
  profileLinkSource: string
): StewardItemProps {
  return stewards.reduce((obj, user) => {
    const { profile_url, user_id, display_name } = user;
    let profileLink = profile_url;
    let isExternalLink = true;
    if (indexUsersEnabled()) {
      isExternalLink = false;
      profileLink = `/user/${user_id}?source=${profileLinkSource}`;
    }
    return {
      ...obj,
      [user_id]: {
        label: display_name,
        link: profileLink,
        isExternal: isExternalLink,
      },
    };
  }, {});
}

/**
 * Creates axios payload for the request to update an steward
 */
export function createStewardUpdatePayload(
  resourceType: ResourceType,
  resourceKey: string,
  payload: UpdateStewardPayload
) {
  const updateStewardEndpointMap = {
    [ResourceType.table]: `${API.API_PATH}/update_table_steward`,
    [ResourceType.feature]: `${API.API_PATH}/update_feature_steward`,
  };
  const url = updateStewardEndpointMap[resourceType];
  if (url === undefined) {
    throw new Error(`Update Steward not supported for ${resourceType}`);
  }
  return {
    url,
    method: payload.method,
    data: {
      key: resourceKey,
      steward: payload.id,
    },
  };
}
