// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

type BadgesWidgetProps = {text: string}
const BadgesListWidget: React.FC<BadgesWidgetProps> = ({text}: BadgesWidgetProps) => (
  <div>foo {text}</div>
)

export default BadgesListWidget;