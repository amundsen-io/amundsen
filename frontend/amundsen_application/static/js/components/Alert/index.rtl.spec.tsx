// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import { NoticeSeverity } from 'config/config-types';

import { Alert, AlertProps, OPEN_PAYLOAD_CTA, PAYLOAD_MODAL_TITLE } from '.';

const setup = (propOverrides?: Partial<AlertProps>) => {
  const props: AlertProps = {
    message: 'Test Message',
    onAction: jest.fn(),
    ...propOverrides,
  };

  render(<Alert {...props} />);

  const user = userEvent.setup();

  return {
    props,
    user,
  };
};

describe('Alert', () => {
  describe('render', () => {
    it('should render an alert icon', () => {
      setup();
      const expected = 1;
      const actual = screen.getAllByTestId('warning-icon').length;

      expect(actual).toBe(expected);
    });

    it('should render the alert message text', () => {
      const { props } = setup();
      const expected = props.message as string;
      const actual = screen.getByText(expected);

      expect(actual).toBeInTheDocument();
    });

    describe('when passing an action text and action handler', () => {
      it('should render the action button', () => {
        setup({ actionText: 'Action Text' });
        const expected = 1;
        const actual = screen.getAllByRole('button').length;

        expect(actual).toBe(expected);
      });

      it('should render the action text', () => {
        const { props } = setup({ actionText: 'Action Text' });
        const actual = screen.getByText(props.actionText as string);

        expect(actual).toBeInTheDocument();
      });
    });

    describe('when passing an action text and action href', () => {
      it('should render the action link', () => {
        setup({
          actionHref: 'http://testSite.com',
          actionText: 'Action Text',
        });
        const expected = 1;
        const actual = screen.getAllByRole('link').length;

        expect(actual).toBe(expected);
      });

      it('should render the action text', () => {
        const { props } = setup({
          actionHref: 'http://testSite.com',
          actionText: 'Action Text',
        });
        const actual = screen.getByText(props.actionText as string);

        expect(actual).toBeInTheDocument();
      });
    });

    describe('when passing a custom action link', () => {
      it('should render the custom action link', () => {
        setup({
          actionLink: (
            <a className="test-action-link" href="http://testSite.com">
              Custom Link
            </a>
          ),
        });
        const expected = 1;
        const actual = screen.getAllByRole('link').length;

        expect(actual).toBe(expected);
      });
    });

    describe('when passing a severity', () => {
      it('should render the warning icon by default', () => {
        setup();
        const expected = 1;
        const actual = screen.getAllByTestId('warning-icon').length;

        expect(actual).toBe(expected);
      });

      it('should render the info icon when info severity', () => {
        setup({ severity: NoticeSeverity.INFO });
        const expected = 1;
        const actual = screen.getAllByTestId('info-icon').length;

        expect(actual).toBe(expected);
      });

      it('should render the alert icon when alert severity', () => {
        setup({ severity: NoticeSeverity.ALERT });
        const expected = 1;
        const actual = screen.getAllByTestId('alert-icon').length;

        expect(actual).toBe(expected);
      });

      it('should render the alert icon when warning severity', () => {
        setup({ severity: NoticeSeverity.WARNING });
        const expected = 1;
        const actual = screen.getAllByTestId('warning-icon').length;

        expect(actual).toBe(expected);
      });
    });

    describe('when passing a payload', () => {
      const testPayload = {
        testKey: 'testValue',
        testKey2: 'testHTMLVAlue <a href="http://lyft.com">Lyft</a>',
      };

      it('should render the "see details" button link', () => {
        setup({ payload: testPayload });
        const seeDetailsButton = screen.getByRole('button', {
          name: OPEN_PAYLOAD_CTA,
        });

        expect(seeDetailsButton).toBeInTheDocument();
      });
    });
  });

  describe('lifetime', () => {
    describe('when clicking on the action button', () => {
      it('should call the onAction handler', () => {
        const handlerSpy = jest.fn();
        const { user } = setup({
          actionText: 'Action Text',
          onAction: handlerSpy,
        });
        const actionButton = screen.getByRole('button');

        user.click(actionButton);

        waitFor(() => {
          expect(handlerSpy).toHaveBeenCalledTimes(1);
        });
      });
    });

    describe('when clicking on the see details button of a payload alert', () => {
      const testPayload = {
        testKey: 'testValue',
        testKey2: 'testHTMLVAlue <a href="http://lyft.com">Lyft</a>',
      };

      it('should call the onAction handler', () => {
        const handlerSpy = jest.fn();
        const { user } = setup({
          onAction: handlerSpy,
          payload: testPayload,
        });

        const seeDetailsButton = screen.getByRole('button', {
          name: OPEN_PAYLOAD_CTA,
        });

        user.click(seeDetailsButton);
        waitFor(() => {
          expect(handlerSpy).toHaveBeenCalledTimes(1);
        });
      });

      it('should render the alert payload modal', () => {
        const { user } = setup({ payload: testPayload });

        user.click(screen.getByText(OPEN_PAYLOAD_CTA));

        waitFor(() => {
          const alertPayloadModal = screen.getByRole('dialog');

          expect(alertPayloadModal).toBeInTheDocument();
        });
      });

      it('should render the alert payload modal header with the payload', () => {
        const { user } = setup({ payload: testPayload });

        user.click(screen.getByText(OPEN_PAYLOAD_CTA));

        waitFor(() => {
          const alertPayloadModalHeader = screen.getByRole('heading', {
            name: PAYLOAD_MODAL_TITLE,
          });

          expect(alertPayloadModalHeader).toBeInTheDocument();
        });
      });

      it('should render the alert payload modal body with the payload', () => {
        const { user } = setup({
          payload: testPayload,
        });
        const expected = 1;

        user.click(screen.getByText(OPEN_PAYLOAD_CTA));

        waitFor(() => {
          const actual = screen.queryAllByTestId('alert-payload').length;

          expect(actual).toEqual(expected);
        });
      });

      it('should render the alert payload modal footer with a close button', () => {
        const { user } = setup({
          payload: testPayload,
        });
        const expected = 1;

        user.click(screen.getByText(OPEN_PAYLOAD_CTA));

        waitFor(() => {
          const actual = screen.queryAllByTestId('alert-payload-close').length;

          expect(actual).toEqual(expected);
        });
      });
    });
  });
});
