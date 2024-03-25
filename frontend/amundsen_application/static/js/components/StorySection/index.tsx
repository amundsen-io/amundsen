// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

const DEFAULT_WIDTH = 600;

export type BlockProps = {
  children: React.ReactNode;
  title: string;
  text?: string | React.ReactNode;
  width?: number;
};

const StorySection: React.FC<BlockProps> = ({
  children,
  text,
  title,
  width = DEFAULT_WIDTH,
}: BlockProps) => (
  <div
    className="story-section"
    style={{ padding: '2em 2em 1em', maxWidth: width }}
  >
    <h1 className="text-headline-w1">{title}</h1>
    {text && <p className="text-body-w1">{text}</p>}
    <div style={{ paddingTop: '1em' }}>{children}</div>
  </div>
);

export default StorySection;
