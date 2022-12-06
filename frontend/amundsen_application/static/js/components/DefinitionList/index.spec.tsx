// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';

import { DefinitionList, DefinitionListProps } from '.';

const setup = (propOverrides?: Partial<DefinitionListProps>) => {
  const props: DefinitionListProps = {
    definitions: [{ term: 'testTerm', description: 'testDescription' }],
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = mount(<DefinitionList {...props} />);

  return {
    props,
    wrapper,
  };
};

describe('DefinitionList', () => {
  describe('render', () => {
    it('should render a definition list', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find('dl').length;

      expect(actual).toEqual(expected);
    });

    it('should render one definition container', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find('.definition-list-container').length;

      expect(actual).toEqual(expected);
    });

    it('should render one definition term', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find('.definition-list-term').length;

      expect(actual).toEqual(expected);
    });

    it('should render one definition definition', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find('.definition-list-definition').length;

      expect(actual).toEqual(expected);
    });

    describe('when passing several definitions', () => {
      it('should render as many containers', () => {
        const { wrapper } = setup({
          definitions: [
            {
              term: 'Table name',
              description: 'coco.fact_rides',
            },
            {
              term: 'Root cause',
              description:
                'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod',
            },
            {
              term: 'Estimate',
              description: 'Target fix by MM/DD/YYYY 00:00',
            },
          ],
        });
        const expected = 3;
        const actual = wrapper.find('.definition-list-container').length;

        expect(actual).toEqual(expected);
      });

      it('should render as many terms-definition pairs', () => {
        const { wrapper } = setup({
          definitions: [
            {
              term: 'Table name',
              description: 'coco.fact_rides',
            },
            {
              term: 'Root cause',
              description:
                'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod',
            },
            {
              term: 'Estimate',
              description: 'Target fix by MM/DD/YYYY 00:00',
            },
          ],
        });
        const expected = 3;
        const actualTerms = wrapper.find('.definition-list-term').length;
        const actualDefinitions = wrapper.find(
          '.definition-list-definition'
        ).length;

        expect(actualTerms).toEqual(expected);
        expect(actualDefinitions).toEqual(expected);
      });
    });

    describe('when passing definitions with html', () => {
      it('should render them', () => {
        const { wrapper } = setup({
          definitions: [
            {
              term: 'Verity checks',
              description:
                '1 out of 4 checks failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
            },
            {
              term: 'Failed DAGs',
              description:
                '1 out of 4 DAGs failed (<a href="http://lyft.com">Link</a> | <a href="http://lyft.com">Ownser</a>)',
            },
          ],
        });
        const expected = 2;
        const actualTerms = wrapper.find('.definition-list-term').length;
        const actualDefinitions = wrapper.find(
          '.definition-list-definition'
        ).length;

        expect(actualTerms).toEqual(expected);
        expect(actualDefinitions).toEqual(expected);
      });
    });

    describe('when passing a custom term width', () => {
      it('should set its width', () => {
        const { wrapper } = setup({
          termWidth: 200,
        });
        const expected = 'min-width: 200px;';
        const actual = wrapper
          .find('.definition-list-term')
          ?.getDOMNode()
          ?.getAttribute('style');

        expect(actual).toEqual(expected);
      });
    });
  });
});
