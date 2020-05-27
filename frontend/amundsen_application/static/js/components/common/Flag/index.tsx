import * as React from 'react';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export enum CaseType {
  LOWER_CASE = 'lowerCase',
  SENTENCE_CASE = 'sentenceCase',
  UPPER_CASE = 'upperCase'
}

export interface FlagProps {
  caseType?: string | null;
  text: string;
  labelStyle?: string;
}

export function convertText(str: string, caseType: string): string {
  str = str || '';
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

const Flag: React.SFC<FlagProps> = ({ caseType, text, labelStyle }) => {
  // TODO: After upgrading to Bootstrap 4, this component should leverage badges
  // https://getbootstrap.com/docs/4.1/components/badge/
  return (
    <span className={`flag label label-${labelStyle}`}>{convertText(text, caseType)}</span>
  );
};

Flag.defaultProps = {
  caseType: null,
  text: '',
  labelStyle: 'default',
};

export default Flag;
