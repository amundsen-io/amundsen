// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { ResourceType, ProviderResource } from 'interfaces';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import BadgeList from 'features/BadgeList';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';
import { logClick } from 'utils/analytics';
import { LoggingParams } from '../types';
import MetadataHighlightList from '../MetadataHighlightList';
import { HighlightedResource } from '../MetadataHighlightList/utils';

export interface ProviderListItemProps {
  provider: ProviderResource;
  logging: LoggingParams;
  providerHighlights: HighlightedResource;
  disabled?: boolean;
}

/*
  this function get's the provider name from the key to preserve original
  capitalization since search needs the names to be lowercase for analysis
*/
export const getName = (provider) => {
  const splitKey = provider.key.split('/');
  const keyName = splitKey[splitKey.length - 1];

  if (keyName.toLowerCase() === provider.name) {
    return keyName;
  }

  return provider.name;
};

export const getLink = (provider, logging) => {
  const name = getName(provider);

  if (provider.link) return provider.link;

  return (
    `/provider_detail/${name}` +
    `?index=${logging.index}&source=${logging.source}`
  );
};

export const generateResourceIconClass = (databaseId: string): string =>
  `icon resource-icon ${getSourceIconClass(databaseId, ResourceType.provider)}`;

const ProviderListItem: React.FC<ProviderListItemProps> = ({
  provider,
  logging,
  providerHighlights,
  disabled,
}) => (
  <li className="list-group-item">
    <Link
      className={`resource-list-item provider-list-item ${
        disabled ? 'is-disabled' : 'clickable'
      }`}
      to={getLink(provider, logging)}
      onClick={(e) =>
        logClick(e, {
          target_id: 'provider_list_item',
          value: logging.source,
          position: logging.index.toString(),
        })
      }
    >
      <div className="resource-info">
        <span className={generateResourceIconClass(provider.name)} />
        <div className="resource-info-text my-auto">
          <div className="resource-name">
            <div className="truncated">
            </div>
            <BookmarkIcon
              bookmarkKey={provider.key}
              resourceType={ResourceType.provider}
            />
          </div>
          <span className="description-section">
            {provider.description && (
              <div
                className="description text-body-w3 truncated"
                dangerouslySetInnerHTML={{
                  __html: providerHighlights.description,
                }}
              />
            )}
          </span>
        </div>
      </div>
      <div className="resource-type resource-source">
        {getSourceDisplayName(provider.name, provider.type)}
      </div>
      <div className="resource-badges">
        {!!provider.badges && provider.badges.length > 0 && (
          <div>
            <div className="body-secondary-3">
              <BadgeList badges={provider.badges} />
            </div>
          </div>
        )}
        <img className="icon icon-right" alt="" />
      </div>
    </Link>
  </li>
);
export default ProviderListItem;
