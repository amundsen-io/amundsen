// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as AnalyticsUtils from './analytics';
import * as NavigationUtils from './navigation';

jest.mock('config/config-utils', () => ({
  getAnalyticsConfig: jest.fn(() => ({ plugins: [] })),
}));

describe('analytics', () => {
  const pageSpy = jest.fn();
  const trackSpy = jest.fn();
  const mockAnalyticsObject = {
    ...AnalyticsUtils.analyticsInstance(),
    page: pageSpy,
    track: trackSpy,
  };
  const mockUrl = 'testUrl';

  beforeAll(() => {
    jest.spyOn(NavigationUtils, 'generateSearchUrl').mockReturnValue(mockUrl);
    jest
      .spyOn(AnalyticsUtils, 'analyticsInstance')
      .mockImplementation(() => mockAnalyticsObject);
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  describe('trackEvent', () => {
    describe('when it is a pageViewActionType', () => {
      it('calls the page method', () => {
        const expected = 1;

        AnalyticsUtils.trackEvent('analytics/pageView', { label: 'test' });

        expect(pageSpy.mock.calls.length).toBe(expected);
        expect(pageSpy.mock.calls[0][0].url).toBe('test');
      });
    });

    describe('when it is an event', () => {
      it('calls the track method', () => {
        const expected = 1;
        const testProperties = { label: 'test' };

        AnalyticsUtils.trackEvent('eventName', testProperties);

        expect(trackSpy.mock.calls.length).toBe(expected);
        expect(trackSpy.mock.calls[0][0]).toBe('eventName');
        expect(trackSpy.mock.calls[0][1]).toBe(testProperties);
      });
    });
  });

  describe('logClick', () => {
    afterEach(() => {
      jest.restoreAllMocks();
    });

    it('logs click events with the id target_id', () => {
      const trackEventSpy = jest.spyOn(AnalyticsUtils, 'trackEvent');
      const mockEvent = {
        currentTarget: {
          id: 'testId',
          nodeName: 'a',
          classList: ['btn'],
        },
      } as unknown as React.MouseEvent<HTMLElement>;
      const expected = mockEvent.currentTarget.id;

      AnalyticsUtils.logClick(mockEvent);

      expect(trackEventSpy.mock.calls.length).toBe(1);
      expect(trackEventSpy.mock.calls[0][1].target_id).toBe(expected);
    });

    describe('when using a data-type attribute', () => {
      it('logs click events with the data-type as target_id', () => {
        const trackEventSpy = jest.spyOn(AnalyticsUtils, 'trackEvent');
        const mockEvent = {
          currentTarget: {
            dataset: {
              type: 'testDatasetType',
            },
            id: 'testId',
            nodeName: 'a',
            classList: ['btn'],
          },
        } as unknown as React.MouseEvent<HTMLElement>;
        const expected = mockEvent.currentTarget.dataset.type;

        AnalyticsUtils.logClick(mockEvent);

        expect(trackEventSpy.mock.calls.length).toBe(1);
        expect(trackEventSpy.mock.calls[0][1].target_id).toBe(expected);
      });
    });

    describe('getNodeName', () => {
      describe('when target is a link', () => {
        it('should return link', () => {
          const link = document.createElement('a');
          const expected = 'link';
          const actual = AnalyticsUtils.getNodeName(link);

          expect(actual).toBe(expected);
        });
      });

      describe('when target is a link with a btn class', () => {
        it('should return link', () => {
          const link = document.createElement('a');

          link.classList.add('btn');
          const expected = 'button';
          const actual = AnalyticsUtils.getNodeName(link);

          expect(actual).toBe(expected);
        });
      });
    });
  });
});
