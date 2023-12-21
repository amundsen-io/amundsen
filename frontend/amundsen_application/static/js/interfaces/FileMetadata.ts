// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { UpdateMethod } from './Enums';
import { User } from './User';
import { Badge } from './Badges';

export interface FileMetadata {
  badges: Badge[];
  key: string;
  name: string;
  description: string;
}

