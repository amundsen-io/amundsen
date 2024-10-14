// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import PopularResources, {
  PopularResourcesProps,
} from 'features/PopularResources';
import * as React from 'react';

type PopularResourcesWidgetProps = PopularResourcesProps;

export const PopularResourcesWidget: React.FC<PopularResourcesWidgetProps> = (
  props: PopularResourcesProps
) => <PopularResources {...props} />;

export default PopularResourcesWidget;
