// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as TextUtils from './text';

describe('text', () => {
  describe('convertText', () => {
    it('converts to lower case', () => {
      const actual = TextUtils.convertText(
        'TESt LoWer cASe',
        TextUtils.CaseType.LOWER_CASE
      );
      const expected = 'test lower case';

      expect(actual).toBe(expected);
    });

    it('converts to sentence case', () => {
      const actual = TextUtils.convertText(
        'tESt sentence cASe',
        TextUtils.CaseType.SENTENCE_CASE
      );
      const expected = 'Test sentence case';

      expect(actual).toBe(expected);
    });

    it('converts to upper case', () => {
      const actual = TextUtils.convertText(
        'test upper cASe',
        TextUtils.CaseType.UPPER_CASE
      );
      const expected = 'TEST UPPER CASE';

      expect(actual).toBe(expected);
    });

    it('converts to title case', () => {
      const actual = TextUtils.convertText(
        'tEST title cASe',
        TextUtils.CaseType.TITLE_CASE
      );
      const expected = 'Test Title Case';

      expect(actual).toBe(expected);
    });

    describe('when caseType is not provided', () => {
      it('returns the input string', () => {
        const expected = 'Test Title Case';
        const actual = TextUtils.convertText(expected, null);

        expect(actual).toBe(expected);
      });
    });

    describe('when string is not provided', () => {
      it('returns an empty string', () => {
        const expected = '';
        const actual = TextUtils.convertText(
          undefined,
          TextUtils.CaseType.TITLE_CASE
        );

        expect(actual).toBe(expected);
      });
    });
  });
});
