// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import PopularResources, {
  PopularResourcesProps,
} from 'features/PopularResources';
import * as React from 'react';

type PopularResourcesWidgetProps = PopularResourcesProps;

class PopularResourcesWidget extends React.Component<PopularResourcesWidgetProps> {
  render() {
    return (
      <div>
        <PopularResources />
      </div>
    );
  }
}

export default PopularResourcesWidget;
