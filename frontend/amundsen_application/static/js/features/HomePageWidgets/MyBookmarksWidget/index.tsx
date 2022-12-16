// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import MyBookmarks, { MyBookmarksProps } from 'features/MyBookmarks';

type MyBookmarksWidgetProps = MyBookmarksProps;

export const MyBookmarksWidget: React.FC<MyBookmarksWidgetProps> = (
  props: MyBookmarksWidgetProps
) => <MyBookmarks {...props} />;

export default MyBookmarksWidget;
