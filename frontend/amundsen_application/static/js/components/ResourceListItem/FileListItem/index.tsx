// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { ResourceType, FileResource } from 'interfaces';

import BookmarkIcon from 'components/Bookmark/BookmarkIcon';

import { getSourceDisplayName, getSourceIconClass } from 'config/config-utils';

import BadgeList from 'features/BadgeList';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';
import { logClick } from 'utils/analytics';
import { LoggingParams } from '../types';
import MetadataHighlightList from '../MetadataHighlightList';
import { HighlightedResource } from '../MetadataHighlightList/utils';

export interface FileListItemProps {
  file: FileResource;
  logging: LoggingParams;
  fileHighlights: HighlightedResource;
  disabled?: boolean;
}

/*
  this function get's the file name from the key to preserve original
  capitalization since search needs the names to be lowercase for analysis
*/
export const getName = (file) => {
  const splitKey = file.key.split('/');
  const keyName = splitKey[splitKey.length - 1];

  if (keyName.toLowerCase() === file.name) {
    return keyName;
  }

  return file.name;
};

export const getLink = (file, logging) => {
  const name = getName(file);

  if (file.link) return file.link;

  return (
    `/file_detail/${name}` +
    `?index=${logging.index}&source=${logging.source}`
  );
};

export const generateResourceIconClass = (databaseId: string): string =>
  `icon resource-icon ${getSourceIconClass(databaseId, ResourceType.file)}`;

const FileListItem: React.FC<FileListItemProps> = ({
  file,
  logging,
  fileHighlights,
  disabled,
}) => (
  <li className="list-group-item">
    <Link
      className={`resource-list-item file-list-item ${
        disabled ? 'is-disabled' : 'clickable'
      }`}
      to={getLink(file, logging)}
      onClick={(e) =>
        logClick(e, {
          target_id: 'file_list_item',
          value: logging.source,
          position: logging.index.toString(),
        })
      }
    >
      <div className="resource-info">
        <span className={generateResourceIconClass(file.name)} />
        <div className="resource-info-text my-auto">
          <div className="resource-name">
            <div className="truncated">
            </div>
            <BookmarkIcon
              bookmarkKey={file.key}
              resourceType={ResourceType.file}
            />
          </div>
          <span className="description-section">
            {file.description && (
              <div
                className="description text-body-w3 truncated"
                dangerouslySetInnerHTML={{
                  __html: fileHighlights.description,
                }}
              />
            )}
          </span>
        </div>
      </div>
      <div className="resource-type resource-source">
        {getSourceDisplayName(file.name, file.type)}
      </div>
      <div className="resource-badges">
        {!!file.badges && file.badges.length > 0 && (
          <div>
            <div className="body-secondary-3">
              <BadgeList badges={file.badges} />
            </div>
          </div>
        )}
        <img className="icon icon-right" alt="" />
      </div>
    </Link>
  </li>
);
export default FileListItem;
