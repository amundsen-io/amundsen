// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import BadgeList from 'features/BadgeList';
import { ResourceType, FeatureResource } from 'interfaces';

import { RightIcon } from 'components/SVGIcons';
import { LogSearchEventRequest } from 'ducks/log/types';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { logSearchEvent } from 'ducks/log/reducer';
import { HighlightedResource } from '../MetadataHighlightList/utils';
import { LoggingParams } from '../types';

export interface OwnProps {
  feature: FeatureResource;
  logging: LoggingParams;
  featureHighlights: HighlightedResource;
}

export interface DispatchFromProps {
  logSearchEvent: (
    resourceLink: string,
    resourceType: ResourceType,
    source: string,
    index: number,
    event: any,
    inline: boolean,
    extra?: { [key: string]: any }
  ) => LogSearchEventRequest;
}

export type FeatureListItemProps = OwnProps & DispatchFromProps;

const getLink = (feature: FeatureResource, logging: LoggingParams) =>
  `/feature/${feature.key}?index=${logging.index}&source=${logging.source}`;

const generateResourceIconClass = (
  featureId: string,
  featureType: ResourceType
): string => `icon resource-icon ${getSourceIconClass(featureId, featureType)}`;

export const FeatureListItem: React.FC<FeatureListItemProps> = ({
  feature,
  logging,
  featureHighlights,
  logSearchEvent,
}: FeatureListItemProps) => {
  const source =
    feature.availability?.length > 0 ? feature.availability[0] : '';

  return (
    <li className="list-group-item clickable">
      <Link
        className="resource-list-item table-list-item"
        to={getLink(feature, logging)}
        data-type="feature_list_item"
        onClick={(e: React.MouseEvent<HTMLAnchorElement>) =>
          logSearchEvent(
            getLink(feature, logging),
            ResourceType.feature,
            logging.source,
            logging.index,
            e,
            false
          )
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

export const mapDispatchToProps = (dispatch: any): DispatchFromProps => {
  const dispatchableActions: DispatchFromProps = bindActionCreators(
    {
      logSearchEvent,
    },
    dispatch
  );

  return dispatchableActions;
};
export default connect<{}, DispatchFromProps, OwnProps>(
  null,
  mapDispatchToProps
)(FeatureListItem);
