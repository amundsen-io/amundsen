// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import { logClick } from 'utils/analytics';

import BadgeList from 'features/BadgeList';
import { ResourceType, FeatureResource } from 'interfaces';

import { LoggingParams } from '../types';

export interface FeatureListItemProps {
  feature: FeatureResource;
  logging: LoggingParams;
}

const getLink = (feature: FeatureResource, logging: LoggingParams) => {
  return `/feature/${feature.key}?index=${logging.index}&source=${logging.source}`;
};

const generateResourceIconClass = (
  featureId: string,
  featureType: ResourceType
): string => `icon resource-icon ${getSourceIconClass(featureId, featureType)}`;

const FeatureListItem: React.FC<FeatureListItemProps> = ({
  feature,
  logging,
}: FeatureListItemProps) => {
  const source = feature.availability.length > 0 ? feature.availability[0] : '';
  return (
    <li className="list-group-item clickable">
      <Link
        className="resource-list-item table-list-item"
        to={getLink(feature, logging)}
        onClick={(e) =>
          logClick(e, {
            target_id: 'feature_list_item',
            value: logging.source,
          })
        }
      >
        <div className="resource-info">
          <span className={generateResourceIconClass(source, feature.type)} />
          <div className="resource-info-text my-auto">
            <div className="resource-name">
              {`${feature.feature_group}.${feature.name}`}
            </div>
            <div className="body-secondary-3 truncated">
              {feature.description}
            </div>
          </div>
        </div>
        <div className="resource-type">
          {getSourceDisplayName(source, feature.type)}
        </div>
        <div className="resource-badges">
          {!!feature.badges && feature.badges.length > 0 && (
            <div className="body-secondary-3">
              <BadgeList badges={feature.badges} />
            </div>
          )}
        </div>
        <div className="resource-entity">
          <div>{feature.entity}</div>
          <img className="icon icon-right" alt="" />
        </div>
      </Link>
    </li>
  );
};

export default FeatureListItem;
