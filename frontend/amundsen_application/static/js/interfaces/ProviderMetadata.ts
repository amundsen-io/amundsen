// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { UpdateMethod } from './Enums';
import { User } from './User';
import { Badge } from './Badges';
import { ProgrammaticDescription } from './TableMetadata'

export interface ProviderMetadata {
  key: string;
  name: string;
  description: string;
  is_editable: boolean;
}

export interface ProviderProgrammaticDescriptions {
  left?: ProgrammaticDescription[];
  right?: ProgrammaticDescription[];
  other?: ProgrammaticDescription[];
}