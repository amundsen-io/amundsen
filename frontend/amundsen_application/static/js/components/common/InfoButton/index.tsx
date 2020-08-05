// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { OverlayTrigger, Popover } from 'react-bootstrap';

// TODO - Consider an alternative to react-sanitized-html (large filesize)
import SanitizedHTML from 'react-sanitized-html';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

const INFO_BUTTON_TEXT = 'More info';

export interface InfoButtonProps {
  infoText?: string;
  title?: string;
  placement?: string;
  size?: string;
}

const InfoButton: React.FC<InfoButtonProps> = ({
  title,
  infoText,
  placement,
  size,
}: InfoButtonProps) => {
  const popoverHoverFocus = (
    <Popover id="popover-trigger-hover-focus" title={title}>
      <SanitizedHTML html={infoText} />
    </Popover>
  );

  return (
    <OverlayTrigger
      trigger={['hover', 'focus']}
      placement={placement}
      overlay={popoverHoverFocus}
    >
      <button className={'btn icon info-button ' + size} type="button">
        <span className="sr-only">{INFO_BUTTON_TEXT}</span>
      </button>
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
