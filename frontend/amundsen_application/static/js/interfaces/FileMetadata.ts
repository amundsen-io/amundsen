// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { Badge } from './Badges';

export interface FileMetadata {
  badges: Badge[];
  key: string;
  name: string;
  description: string;
  is_editable: boolean;
}

