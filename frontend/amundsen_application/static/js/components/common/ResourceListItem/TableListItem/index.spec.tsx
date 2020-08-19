// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import SchemaInfo from 'components/common/ResourceListItem/SchemaInfo';
import { ResourceType, TagType } from 'interfaces';

import * as ConfigUtils from 'config/config-utils';
import BadgeList from 'components/common/BadgeList';
import TableListItem, { TableListItemProps } from '.';

const MOCK_DISPLAY_NAME = 'displayName';
const MOCK_ICON_CLASS = 'test-class';

jest.mock('config/config-utils', () => ({
  getSourceDisplayName: () => {
    return MOCK_DISPLAY_NAME;
  },
  getSourceIconClass: () => {
    return MOCK_ICON_CLASS;
  },
}));

const getDBIconClassSpy = jest.spyOn(ConfigUtils, 'getSourceIconClass');

describe('TableListItem', () => {
  const setup = (propOverrides?: Partial<TableListItemProps>) => {
    const props: TableListItemProps = {
      logging: { source: 'src', index: 0 },
      table: {
        type: ResourceType.table,
        cluster: '',
        database: 'testdb',
        description: 'I am the description',
        key: '',
        last_updated_timestamp: 1553829681,
        badges: [{ tag_name: 'badgeName', tag_type: TagType.BADGE }],
        name: 'tableName',
        schema: 'tableSchema',
        schema_description: 'schemaDescription',
      },
      ...propOverrides,
    };
    const wrapper = shallow<TableListItem>(<TableListItem {...props} />);
    return { props, wrapper };
  };

  describe('getLink', () => {
    it('getLink returns correct string', () => {
      const { props, wrapper } = setup();
      const { table, logging } = props;
      expect(wrapper.instance().getLink()).toEqual(
        `/table_detail/${table.cluster}/${table.database}/${table.schema}/${table.name}?index=${logging.index}&source=${logging.source}`
      );
    });
  });

  describe('generateResourceIconClass', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper;
    });
    it('calls getSourceIconClass with given database id', () => {
      const testValue = 'noEffectOnTest';
      const givenResource = ResourceType.table;

      wrapper.instance().generateResourceIconClass(testValue, givenResource);

      expect(getDBIconClassSpy).toHaveBeenCalledWith(testValue, givenResource);
    });

    it('returns the default classes with the correct icon class appended', () => {
      const iconClass = wrapper
        .instance()
        .generateResourceIconClass('noEffectOnTest');

      expect(iconClass).toEqual(`icon resource-icon test-class`);
    });
  });

  describe('render', () => {
    let props: TableListItemProps;
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
          wrapper.instance().generateResourceIconClass(props.table.database)
        );
      });

      describe('if props.table has schema description', () => {
        let schemaInfo;
        beforeAll(() => {
          schemaInfo = resourceInfo.find(SchemaInfo);
        });

        it('renders table name schema and description', () => {
          expect(schemaInfo.props()).toMatchObject({
            schema: props.table.schema,
            table: props.table.name,
            desc: props.table.schema_description,
          });
        });
      });

      describe('if props.table not have schema description', () => {
        it('if schema description is empty string', () => {
          const { wrapper } = setup({
            table: {
              type: ResourceType.table,
              cluster: '',
              database: 'testdb',
              description: 'I am the description',
              key: '',
              last_updated_timestamp: 1553829681,
              badges: [{ tag_name: 'badgeName', tag_type: TagType.BADGE }],
              name: 'tableName',
              schema: 'tableSchema',
              schema_description: '',
            },
          });
          expect(
            wrapper.find('.resource-name').children().at(0).text()
          ).toEqual('tableSchema.tableName');
        });

        it('if schema description is null', () => {
          const { wrapper } = setup({
            table: {
              type: ResourceType.table,
              cluster: '',
              database: 'testdb',
              description: 'I am the description',
              key: '',
              last_updated_timestamp: 1553829681,
              badges: [{ tag_name: 'badgeName', tag_type: TagType.BADGE }],
              name: 'tableName',
              schema: 'tableSchema',
              schema_description: null,
            },
          });
          expect(
            wrapper.find('.resource-name').children().at(0).text()
          ).toEqual('tableSchema.tableName');
        });
      });

      it('renders a bookmark icon in the resource name with correct props', () => {
        const elementProps = resourceInfo
          .find('.resource-name')
          .find(BookmarkIcon)
          .props();
        expect(elementProps.bookmarkKey).toBe(props.table.key);
        expect(elementProps.resourceType).toBe(props.table.type);
      });

      it('renders table description', () => {
        expect(resourceInfo.children().at(1).children().at(1).text()).toEqual(
          'I am the description'
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
            props.table.database,
            props.table.type
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

      describe('if props.table has badges', () => {
        it('renders BadgeList for badges', () => {
          expect(resourceBadges.find(BadgeList).props().badges).toEqual(
            props.table.badges
          );
        });
      });

      describe('if props.table does not have badges', () => {
        it('does not render badges section', () => {
          const { wrapper } = setup({
            table: {
              type: ResourceType.table,
              cluster: '',
              database: '',
              description: 'I am the description',
              key: '',
              badges: null,
              name: 'tableName',
              schema: 'tableSchema',
              schema_description: 'schemaDescription',
            },
          });
          expect(wrapper.find('.resource-badges').children()).toHaveLength(1);
        });

        it('or if they are empty does not render badges section', () => {
          const { wrapper } = setup({
            table: {
              type: ResourceType.table,
              cluster: '',
              database: '',
              description: 'I am the description',
              key: '',
              badges: [],
              name: 'tableName',
              schema: 'tableSchema',
              schema_description: 'schemaDescription',
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
