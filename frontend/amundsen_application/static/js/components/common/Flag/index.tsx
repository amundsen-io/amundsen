import * as React from 'react';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

interface FlagProps {
  text: string;
  labelStyle?: string;
}

const Flag: React.SFC<FlagProps> = ({ text, labelStyle }) => {
  // TODO: After upgrading to Bootstrap 4, this component should leverage badges
  // https://getbootstrap.com/docs/4.1/components/badge/
  return (
    <span className={`flag label ${labelStyle}`}>{text.toUpperCase()}</span>
  );
};

Flag.defaultProps = {
  text: '',
  labelStyle: 'label-default',
};

export default Flag;
