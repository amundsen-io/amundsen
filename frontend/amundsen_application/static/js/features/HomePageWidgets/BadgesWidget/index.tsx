// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import BadgesList, { BadgesListContainerProps } from 'features/Badges'


type BadgesWidgetProps = BadgesListContainerProps;

class BadgesListWidget extends React.Component<BadgesWidgetProps> { // TODO change to BadgesListContainerProps
  render() {
    return(
      <div><BadgesList shortBadgesList/></div> 
    );

  }
}

export default BadgesListWidget;