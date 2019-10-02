import * as React from 'react';

import './styles.scss';

export interface FlashMessageProps {
  iconClass?: string | null;
  message: string;
  onClose: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

const FlashMessage: React.SFC<FlashMessageProps> = ({ iconClass, message, onClose }) => {
  return (
    <div className="flash-message">
      {
        iconClass &&
        <img className={`icon ${iconClass}`}/>
      }
      <div className="message">
        { message }
      </div>
      <button type="button" className="btn btn-close" aria-label={"Close"} onClick={onClose}/>
    </div>
  );
};

FlashMessage.defaultProps = {
  iconClass: null,
};

export default FlashMessage;
