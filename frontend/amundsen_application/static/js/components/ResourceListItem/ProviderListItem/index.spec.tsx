// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import BookmarkIcon from 'components/Bookmark/BookmarkIcon';
import SchemaInfo from 'components/ResourceListItem/SchemaInfo';
import { ResourceType } from 'interfaces';

import * as ConfigUtils from 'config/config-utils';
import BadgeList from 'features/BadgeList';
import ProviderListItem, {
  ProviderListItemProps,
  getLink,
  generateResourceIconClass,
  getName,
} from '.';

const MOCK_DISPLAY_NAME = 'displayName';
const MOCK_ICON_CLASS = 'test-class';

jest.mock('config/config-utils', () => ({
  getSourceDisplayName: () => MOCK_DISPLAY_NAME,
  getSourceIconClass: () => MOCK_ICON_CLASS,
  getFilterConfigByResource: jest.fn(),
}));

const getDBIconClassSpy = jest.spyOn(ConfigUtils, 'getSourceIconClass');

describe('ProviderListItem', () => {
  const setup = (propOverrides?: Partial<ProviderListItemProps>) => {
    const props: ProviderListItemProps = {
      logging: {
        source: 'src',
        index: 0,
      },
      provider: {
        type: ResourceType.data_provider,
        description: 'I am the description',
        key: '',
        badges: [
          {
            tag_name: 'badgeName',
          },
        ],
        name: 'providerName',
      },
      providerHighlights: {
        name: 'providerName',
        description: 'I am the description',
      },
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow(<ProviderListItem {...props} />);

    return {
      props,
      wrapper,
    };
  };

  describe('getName', () => {
    it('gets name from key with correct capitalization', () => {
      const provider = {
        type: ResourceType.data_provider,
        description: 'I am the description',
        key: 'testdb://provider_NAME',
        badges: [
          {
            tag_name: 'badge_name',
          },
        ],
        name: 'provider_name',
      };

      expect(getName(provider)).toEqual('provider_NAME');
    });
  });

  describe('getLink', () => {
    it('getLink returns correct string', () => {
      const { props } = setup();
      const { provider, logging } = props;

      expect(getLink(provider, logging)).toEqual(
        `/provider_detail/${provider.name}?index=${logging.index}&source=${logging.source}`
      );
    });

    it('should have alternative link', () => {
      const expected = `search?resource=provider&index=0&filters={"is_prioritized":{"value":"false"},"is_view":{"value":"false"},"provider":{"value":"providerName_*"}}`;
      const { props } = setup();
      const { provider, logging } = props;
      const providerWithLink = {
        ...provider,
        link: expected,
      };

      expect(getLink(providerWithLink, logging)).toEqual(expected);
    });
  });

  describe('generateResourceIconClass', () => {
    it('calls getSourceIconClass with given database id', () => {
      const testValue = 'noEffectOnTest';
      const givenResource = ResourceType.data_provider;

      generateResourceIconClass(testValue);

      expect(getDBIconClassSpy).toHaveBeenCalledWith(testValue, givenResource);
    });

    it('returns the default classes with the correct icon class appended', () => {
      const iconClass = generateResourceIconClass('noEffectOnTest');

      expect(iconClass).toEqual(`icon resource-icon test-class`);
    });
  });

  describe('render', () => {
    let props: ProviderListItemProps;
    let wrapper;

    beforeAll(() => {
      const setupResult = setup();

      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders item as Link', () => {
      expect(wrapper.find(Link).exists()).toBeTruthy();
    });

    describe('renders resource-info section', () => {
      let resourceInfo;

      beforeAll(() => {
        resourceInfo = wrapper.find('.resource-info');
      });

      it('renders start correct icon', () => {
        const startIcon = resourceInfo.find('.resource-icon');

        expect(startIcon.exists()).toBe(true);
        expect(startIcon.props().className).toEqual(
          generateResourceIconClass(props.provider.name)
        );
      });

      it('renders a bookmark icon in the resource name with correct props', () => {
        const elementProps = resourceInfo
          .find('.resource-name')
          .find(BookmarkIcon)
          .props();

        expect(elementProps.bookmarkKey).toBe(props.provider.key);
        expect(elementProps.resourceType).toBe(props.provider.type);
      });

      it('renders provider description', () => {
        expect(
          resourceInfo.find('.description-section').render().text()
        ).toEqual('I am the description');
      });
    });

    describe('renders resource-type section', () => {
      let resourceType;

      beforeAll(() => {
        resourceType = wrapper.find('.resource-type');
      });

      it('renders resource type', () => {
        expect(resourceType.text()).toEqual(
          ConfigUtils.getSourceDisplayName(
            props.provider.name,
            props.provider.type
          )
        );
      });
    });

    describe('renders resource-badges section', () => {
      let resourceBadges;

      beforeAll(() => {
        resourceBadges = wrapper.find('.resource-badges');
      });

      it('renders resource badges section', () => {
        expect(resourceBadges.exists()).toBe(true);
      });

      describe('if props.provider has badges', () => {
        it('renders BadgeList for badges', () => {
          expect(resourceBadges.find(BadgeList).props().badges).toEqual(
            props.provider.badges
          );
        });
      });

      describe('if props.provider does not have badges', () => {
        it('does not render badges section', () => {
          const { wrapper } = setup({
            provider: {
              type: ResourceType.data_provider,
              description: 'I am the description',
              key: '',
              badges: undefined,
              name: 'providerName',
            },
          });

          expect(wrapper.find('.resource-badges').children()).toHaveLength(1);
        });

        it('or if they are empty does not render badges section', () => {
          const { wrapper } = setup({
            provider: {
              type: ResourceType.data_provider,
              description: 'I am the description',
              key: '',
              badges: [],
              name: 'providerName',
            },
          });

          expect(wrapper.find('.resource-badges').children()).toHaveLength(1);
        });
      });

      it('renders correct end icon', () => {
        const expectedClassName = 'icon icon-right';

        expect(resourceBadges.find('img').props().className).toEqual(
          expectedClassName
        );
      });
    });
  });
});
