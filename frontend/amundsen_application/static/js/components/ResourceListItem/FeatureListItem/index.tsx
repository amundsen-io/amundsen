// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';
import { logClick } from 'utils/analytics';

import BadgeList from 'features/BadgeList';
import { ResourceType, FeatureResource } from 'interfaces';

import { RightIcon } from 'components/SVGIcons';
import { LoggingParams } from '../types';
import { HighlightedResource } from '../MetadataHighlightList/utils';

export interface FeatureListItemProps {
  feature: FeatureResource;
  logging: LoggingParams;
  featureHighlights: HighlightedResource;
}

const getLink = (feature: FeatureResource, logging: LoggingParams) =>
  `/feature/${feature.key}?index=${logging.index}&source=${logging.source}`;

const generateResourceIconClass = (
  featureId: string,
  featureType: ResourceType
): string => `icon resource-icon ${getSourceIconClass(featureId, featureType)}`;

const FeatureListItem: React.FC<FeatureListItemProps> = ({
  feature,
  logging,
  featureHighlights,
}: FeatureListItemProps) => {
  const source =
    feature.availability?.length > 0 ? feature.availability[0] : '';
  return (
    <li className="list-group-item clickable">
      <Link
        className="resource-list-item table-list-item"
        to={getLink(feature, logging)}
        onClick={(e) =>
          logClick(e, {
            target_id: 'feature_list_item',
            value: logging.source,
            position: logging.index.toString(),
          })
        }
      >
        <div className="resource-info">
          <span className={generateResourceIconClass(source, feature.type)} />
          <div className="resource-info-text my-auto">
            <h3 className="resource-name">
              {`${feature.feature_group}.${feature.name}.${feature.version}`}
            </h3>
            <span className="description-section">
              {feature.description && (
                <div
                  className="description text-body-w3 truncated"
                  dangerouslySetInnerHTML={{
                    __html: featureHighlights.description,
                  }}
                />
              )}
            </span>
          </div>
        </div>
        <div className="resource-type resource-source">
          {getSourceDisplayName(source, feature.type)}
        </div>
        <div className="resource-badges">
          {!!feature.badges && feature.badges.length > 0 && (
            <BadgeList badges={feature.badges} />
          )}
        </div>
        <div className="resource-entity">
          <p className="resource-type">{feature.entity}</p>
          <span className="icon-right">
            <RightIcon />
          </span>
        </div>
      </Link>
    </li>
  );
};

export default FeatureListItem;
