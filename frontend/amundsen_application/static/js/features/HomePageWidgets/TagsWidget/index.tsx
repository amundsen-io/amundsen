// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import TagsListContainer, { TagsListContainerProps } from 'features/Tags';

type TagsWidgetProps = TagsListContainerProps;

export const TagsWidget: React.FC<TagsWidgetProps> = (
  props: TagsWidgetProps
) => <TagsListContainer {...props} />;

export default TagsWidget;
