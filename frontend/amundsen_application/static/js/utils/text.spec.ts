// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as TextUtils from './textUtils';

describe('text', () => {
  describe('convertText', () => {
    it('converts to lower case', () => {
      const actual = TextUtils.convertText(
        'TESt LoWer cASe',
        TextUtils.CaseType.LOWER_CASE
      );
      const expected = 'test lower case';

      expect(actual).toEqual(expected);
    });

    it('converts to sentence case', () => {
      const actual = TextUtils.convertText(
        'tESt sentence cASe',
        TextUtils.CaseType.SENTENCE_CASE
      );
      const expected = 'Test sentence case';

      expect(actual).toEqual(expected);
    });

    it('converts to upper case', () => {
      const actual = TextUtils.convertText(
        'test upper cASe',
        TextUtils.CaseType.UPPER_CASE
      );
      const expected = 'TEST UPPER CASE';

      expect(actual).toEqual(expected);
    });

    it('converts to title case', () => {
      const actual = TextUtils.convertText(
        'tEST title cASe',
        TextUtils.CaseType.TITLE_CASE
      );
      const expected = 'Test Title Case';

      expect(actual).toEqual(expected);
    });

    describe('when caseType is not provided', () => {
      it('returns the input string', () => {
        const expected = 'Test Title Case';
        const actual = TextUtils.convertText(expected, null);

        expect(actual).toEqual(expected);
      });
    });

    describe('when string is not provided', () => {
      it('returns an empty string', () => {
        const expected = undefined;
        const actual = TextUtils.convertText(
          expected,
          TextUtils.CaseType.TITLE_CASE
        );

        expect(actual).toEqual('');
      });
    });
  });
});
