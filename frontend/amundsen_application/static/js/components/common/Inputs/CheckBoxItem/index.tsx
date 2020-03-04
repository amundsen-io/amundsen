import * as React from 'react';
import { connect } from 'react-redux';

import 'components/common/Inputs/styles.scss';

export interface CheckBoxItemProps {
  checked?: boolean;
  disabled?: boolean
  name: string;
  onChange: (e: React.FormEvent<HTMLInputElement>) => any;
  value: string;
}

const CheckBoxItem: React.SFC<CheckBoxItemProps> = ({ checked = false, disabled = false, name, onChange, value, children }) => {
  return (
    <div className="checkbox">
      <label className="checkbox-label">
        <input
          type="checkbox"
          checked={ checked }
          disabled={ disabled }
          name={ name }
          onChange={ onChange }
          value={ value }
        />
        { children }
      </label>
    </div>
  );
};

export default CheckBoxItem;
