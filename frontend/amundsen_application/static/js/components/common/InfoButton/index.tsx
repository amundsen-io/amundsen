import * as React from 'react';
import { OverlayTrigger, Popover } from 'react-bootstrap';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface InfoButtonProps {
  infoText?: string;
  title?: string;
  placement?: string;
  size?: string;
}

const InfoButton: React.SFC<InfoButtonProps> = ({ title, infoText, placement, size }) => {
  const popoverHoverFocus = (
   <Popover id="popover-trigger-hover-focus" title={ title }>
     { infoText }
   </Popover>
 );

  return (
    <OverlayTrigger
     trigger={['hover', 'focus']}
     placement={ placement }
     overlay={popoverHoverFocus}
     >
      <button className={"btn icon info-button " + size}/>
    </OverlayTrigger>
  );
};

InfoButton.defaultProps = {
  infoText: '',
  title: '',
  placement: 'right',
  size: '',
};

export default InfoButton;
