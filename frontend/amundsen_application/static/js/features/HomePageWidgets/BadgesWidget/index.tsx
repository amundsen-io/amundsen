// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import BadgesList, { BadgesListContainerProps } from 'features/Badges';

type BadgesWidgetProps = BadgesListContainerProps;

export const BadgesWidget: React.FC<BadgesWidgetProps> = (
  props: BadgesWidgetProps
) => <BadgesList {...props} />;

export default BadgesWidget;
