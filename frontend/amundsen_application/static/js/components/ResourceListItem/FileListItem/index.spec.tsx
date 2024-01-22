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
import FileListItem, {
  FileListItemProps,
  getLink,
  generateResourceIconClass,
} from '.';

const MOCK_DISPLAY_NAME = 'displayName';
const MOCK_ICON_CLASS = 'test-class';

jest.mock('config/config-utils', () => ({
  getSourceDisplayName: () => MOCK_DISPLAY_NAME,
  getSourceIconClass: () => MOCK_ICON_CLASS,
  getFilterConfigByResource: jest.fn(),
}));

const getDBIconClassSpy = jest.spyOn(ConfigUtils, 'getSourceIconClass');

describe('FileListItem', () => {
  const setup = (propOverrides?: Partial<FileListItemProps>) => {
    const props: FileListItemProps = {
      logging: {
        source: 'src',
        index: 0,
      },
      file: {
        type: ResourceType.file,
        description: 'I am the description',
        key: '',
        badges: [
          {
            tag_name: 'badgeName',
          },
        ],
        name: 'fileName',
      },
      fileHighlights: {
        name: 'fileName',
        description: 'I am the description',
      },
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow(<FileListItem {...props} />);

    return {
      props,
      wrapper,
    };
  };

  describe('getLink', () => {
    it('getLink returns correct string', () => {
      const { props } = setup();
      const { file, logging } = props;

      expect(getLink(file, logging)).toEqual(
        `/file_detail/${file.name}?index=${logging.index}&source=${logging.source}`
      );
    });

    it('should have alternative link', () => {
      const expected = `search?resource=file&index=0&filters={"is_prioritized":{"value":"false"},"is_view":{"value":"false"},"file":{"value":"fileName_*"}}`;
      const { props } = setup();
      const { file, logging } = props;
      const fileWithLink = {
        ...file,
        link: expected,
      };

      expect(getLink(fileWithLink, logging)).toEqual(expected);
    });
  });

  describe('generateResourceIconClass', () => {
    it('calls getSourceIconClass with given database id', () => {
      const testValue = 'noEffectOnTest';
      const givenResource = ResourceType.file;

      generateResourceIconClass(testValue);

      expect(getDBIconClassSpy).toHaveBeenCalledWith(testValue, givenResource);
    });

    it('returns the default classes with the correct icon class appended', () => {
      const iconClass = generateResourceIconClass('noEffectOnTest');

      expect(iconClass).toEqual(`icon resource-icon test-class`);
    });
  });

  describe('render', () => {
    let props: FileListItemProps;
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
          generateResourceIconClass(props.file.name)
        );
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
            props.file.name,
            props.file.type
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

      describe('if props.file has badges', () => {
        it('renders BadgeList for badges', () => {
          expect(resourceBadges.find(BadgeList).props().badges).toEqual(
            props.file.badges
          );
        });
      });

      describe('if props.file does not have badges', () => {
        it('does not render badges section', () => {
          const { wrapper } = setup({
            file: {
              type: ResourceType.file,
              description: 'I am the description',
              key: '',
              badges: undefined,
              name: 'fileName',
            },
          });

          expect(wrapper.find('.resource-badges').children()).toHaveLength(1);
        });

        it('or if they are empty does not render badges section', () => {
          const { wrapper } = setup({
            file: {
              type: ResourceType.file,
              description: 'I am the description',
              key: '',
              badges: [],
              name: 'fileName',
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
