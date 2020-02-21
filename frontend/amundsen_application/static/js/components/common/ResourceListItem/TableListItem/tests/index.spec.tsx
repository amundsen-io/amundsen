import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import TableListItem, { TableListItemProps } from '../';
import { ResourceType } from 'interfaces';

import * as ConfigUtils from 'config/config-utils';

const MOCK_DISPLAY_NAME = 'displayName';
const MOCK_ICON_CLASS = 'test-class';

jest.mock('config/config-utils', () => (
  {
    getDatabaseDisplayName: () => { return MOCK_DISPLAY_NAME },
    getDatabaseIconClass: () => { return MOCK_ICON_CLASS }
  }
));

const getDBIconClassSpy = jest.spyOn(ConfigUtils, 'getDatabaseIconClass');

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
        name: 'tableName',
        schema: 'tableSchema',
      },
      ...propOverrides
    };
    const wrapper = shallow<TableListItem>(<TableListItem {...props} />);
    return { props, wrapper };
  };

  /* Note: Jest is configured to use UTC */
  describe('getDateLabel', () => {
    it('getDateLabel returns correct string', () => {
      const { props, wrapper } = setup();
      expect(wrapper.instance().getDateLabel()).toEqual('Mar 29, 2019');
    });
  });

  describe('getLink', () => {
    it('getLink returns correct string', () => {
      const { props, wrapper } = setup();
      const { table, logging } = props;
      expect(wrapper.instance().getLink()).toEqual(`/table_detail/${table.cluster}/${table.database}/${table.schema}/${table.name}?index=${logging.index}&source=${logging.source}`);
    });
  });

  describe('generateResourceIconClass', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper;
    });
    it('calls getDatabaseIconClass with given database id', () => {
      const testValue = 'noEffectOnTest';
      const iconClass = wrapper.instance().generateResourceIconClass(testValue);
      expect(getDBIconClassSpy).toHaveBeenCalledWith(testValue);
    });

    it('returns the default classes with the correct icon class appended', () => {
      const iconClass = wrapper.instance().generateResourceIconClass('noEffectOnTest');
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
        const startIcon = resourceInfo.find('img');
        expect(startIcon.exists()).toBe(true);
        expect(startIcon.props().className).toEqual(wrapper.instance().generateResourceIconClass(props.table.database));
      });

      it('renders table name', () => {
        expect(resourceInfo.find('.resource-name').children().at(0).text()).toEqual('tableSchema.tableName');
      });

      it('renders a bookmark icon in the resource name', () => {
        expect(resourceInfo.find('.resource-name').find(BookmarkIcon).exists()).toBe(true);
      });

      it('renders table description', () => {
        expect(resourceInfo.children().at(1).children().at(1).text()).toEqual('I am the description');
      });
    });

    describe('renders resource-type section', () => {
      let resourceType;
      beforeAll(() => {
        resourceType = wrapper.find('.resource-type');
      });

      it('renders resource type', () => {
        expect(resourceType.text()).toEqual(ConfigUtils.getDatabaseDisplayName(props.table.database));
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

      describe('if props.table has last_updated_timestamp', () => {
        it('renders Last Updated title', () => {
          expect(resourceBadges.children().at(0).children().at(0).text()).toEqual('Last Updated');
        });

        it('renders getDateLabel value', () => {
          expect(resourceBadges.children().at(0).children().at(1).text()).toEqual(wrapper.instance().getDateLabel());
        });
      });

      describe('if props.table does not have last_updated_timestamp', () => {
        it('does not render Last Updated section', () => {
          const { props, wrapper } = setup({ table: {
            type: ResourceType.table,
            cluster: '',
            database: '',
            description: 'I am the description',
            key: '',
            last_updated_timestamp: null,
            name: 'tableName',
            schema: 'tableSchema',
          }});
          expect(wrapper.find('.resource-badges').children()).toHaveLength(1);
        });
      });

      it('renders correct end icon', () => {
        const expectedClassName = 'icon icon-right'
        expect(resourceBadges.find('img').props().className).toEqual(expectedClassName);
      });
    });
  });
});
