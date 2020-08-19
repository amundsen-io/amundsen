// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { shallow } from 'enzyme';

import { BadgeStyle } from 'config/config-types';
import Flag, { CaseType, FlagProps, convertText } from '.';

describe('Flag', () => {
  let props: FlagProps;
  let subject;

  beforeEach(() => {
    props = {
      text: 'Testing',
    };
    subject = shallow(<Flag {...props} />);
  });

  describe('render', () => {
    it('renders span with correct default className', () => {
      expect(subject.find('span').props().className).toEqual(
        `flag label label-${BadgeStyle.DEFAULT}`
      );
    });

    it('renders span with correct custom className', () => {
      props.labelStyle = BadgeStyle.PRIMARY;
      subject.setProps(props);
      expect(subject.find('span').props().className).toEqual(
        `flag label label-${BadgeStyle.PRIMARY}`
      );
    });

    it('renders span with correct text', () => {
      expect(subject.find('span').text()).toEqual(props.text);
    });
  });

  describe('convertText', () => {
    let text;
    beforeEach(() => {
      text = 'RandOM teXT';
    });
    it('returns lowercase text if caseType=CaseType.LOWER_CASE', () => {
      expect(convertText(text, CaseType.LOWER_CASE)).toEqual('random text');
    });

    it('returns UPPERCASE text if caseType=CaseType.UPPER_CASE', () => {
      expect(convertText(text, CaseType.UPPER_CASE)).toEqual('RANDOM TEXT');
    });

    it('returns Sentence case text if caseType=CaseType.SENTENCE_CASE', () => {
      expect(convertText(text, CaseType.SENTENCE_CASE)).toEqual('Random text');
    });

    it('returns text in defauilt case', () => {
      expect(convertText(text, 'not a valid options')).toEqual(text);
    });

    it('returns empty strings for undefined values', () => {
      expect(convertText(undefined, CaseType.SENTENCE_CASE)).toEqual('');
    });
  });
});
