// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

// TODO: Use css-modules instead of 'import'
import './styles.scss';
import { BadgeStyle } from 'config/config-types';

export enum CaseType {
  LOWER_CASE = 'lowerCase',
  SENTENCE_CASE = 'sentenceCase',
  UPPER_CASE = 'upperCase',
}

export interface FlagProps {
  caseType?: string | null;
  text: string;
  labelStyle?: BadgeStyle;
}

export function convertText(str = '', caseType: string): string {
  switch (caseType) {
    case CaseType.LOWER_CASE:
      return str.toLowerCase();
    case CaseType.SENTENCE_CASE:
      return `${str.charAt(0).toUpperCase()}${str.slice(1).toLowerCase()}`;
    case CaseType.UPPER_CASE:
      return str.toUpperCase();
    default:
      return str;
  }
}

const Flag: React.FC<FlagProps> = ({
  caseType = null,
  text = '',
  labelStyle = BadgeStyle.DEFAULT,
}: FlagProps) => {
  // TODO: After upgrading to Bootstrap 4, this component should leverage badges
  // https://getbootstrap.com/docs/4.1/components/badge/
  return (
    <span className={`flag label label-${labelStyle}`}>
      <div className={`badge-overlay-${labelStyle}`}>
        {convertText(text, caseType)}
      </div>
    </span>
  );
};

export default Flag;
