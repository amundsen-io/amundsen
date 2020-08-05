// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as DocumentTitle from 'react-document-title';

import { shallow } from 'enzyme';

import TagsList from 'components/common/TagsList';
import { BrowsePage } from '..';

describe('BrowsePage', () => {
  const setup = () => {
    return shallow<BrowsePage>(<BrowsePage />);
  };
  let wrapper;

  beforeAll(() => {
    wrapper = setup();
  });

  describe('render', () => {
    it('renders DocumentTitle w/ correct title', () => {
      expect(wrapper.find(DocumentTitle).props().title).toEqual(
        'Browse - Amundsen'
      );
    });

    it('renders correct header', () => {
      expect(wrapper.find('#browse-header').text()).toEqual('Browse Tags');
    });

    it('renders <hr>', () => {
      expect(wrapper.contains(<hr className="header-hr" />));
    });

    it('contains TagsList', () => {
      expect(wrapper.contains(<TagsList />));
    });
  });
});
