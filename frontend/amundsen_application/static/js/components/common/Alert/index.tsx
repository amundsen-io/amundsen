// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { AlertIcon, IconSizes } from '../SVGIcons';

import './styles.scss';

const STROKE_COLOR = '#b8072c'; // $red70

export interface AlertProps {
  message: string | React.ReactNode;
  actionLink?: React.ReactNode;
  actionText?: string;
  actionHref?: string;
  onAction?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

const Alert: React.FC<AlertProps> = ({
  message,
  onAction,
  actionText,
  actionHref,
  actionLink,
}: AlertProps) => {
  let action: null | React.ReactNode = null;

  if (actionText && onAction) {
    action = (
      <span className="alert-action">
        <button type="button" className="btn btn-link" onClick={onAction}>
          {actionText}
        </button>
      </span>
    );
  }

  if (actionText && actionHref) {
    action = (
      <span className="alert-action">
        <a className="action-link" href={actionHref}>
          {actionText}
        </a>
      </span>
    );
  }

  if (actionLink) {
    action = <span className="alert-action">{actionLink}</span>;
  }

  return (
    <div className="alert">
      <AlertIcon stroke={STROKE_COLOR} size={IconSizes.SMALL} />
      <p className="alert-message">{message}</p>
      {action}
    </div>
  );
};

export default Alert;
