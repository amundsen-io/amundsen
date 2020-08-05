// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as Constants from './constants';

import './styles.scss';

export interface FlashMessageProps {
  iconClass?: string | null;
  message: string;
  onClose: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

const FlashMessage: React.FC<FlashMessageProps> = ({
  iconClass,
  message,
  onClose,
}: FlashMessageProps) => {
  return (
    <div className="flash-message">
      {iconClass && <img className={`icon ${iconClass}`} alt="" />}
      <div className="message">{message}</div>
      <button type="button" className="btn btn-close" onClick={onClose}>
        <span className="sr-only">{Constants.CLOSE}</span>
      </button>
    </div>
  );
};

FlashMessage.defaultProps = {
  iconClass: null,
};

export default FlashMessage;
