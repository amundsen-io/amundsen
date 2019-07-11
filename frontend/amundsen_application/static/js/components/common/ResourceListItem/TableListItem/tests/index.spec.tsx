import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import BookmarkIcon from 'components/common/Bookmark/BookmarkIcon';
import TableListItem, { TableListItemProps } from '../';
import { ResourceType } from 'interfaces';

describe('TableListItem', () => {
  const setup = (propOverrides?: Partial<TableListItemProps>) => {
    const props: TableListItemProps = {
      logging: { source: 'src', index: 0 },
      table: {
        type: ResourceType.table,
        cluster: '',
        database: '',
        description: 'I am the description',
        key: '',
        last_updated_epoch: 1553829681,
        name: 'tableName',
        schema_name: 'tableSchema',
      },
      ...propOverrides
    };
    const wrapper = shallow<TableListItem>(<TableListItem {...props} />);
    return { props, wrapper };
  };

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

    it('renders table name', () => {
      expect(wrapper.find('.resource-name').children().at(0).text()).toEqual('tableSchema.tableName');
    });

    it('renders a bookmark icon', () => {
      expect(wrapper.find(BookmarkIcon).exists()).toBe(true);
    });

    it('renders table description', () => {
      expect(wrapper.find('.content').children().at(0).children().at(1).text()).toEqual('I am the description');
    });

    describe('if props.table has last_updated_epoch', () => {
      it('renders Last Update title', () => {
        expect(wrapper.find('.content').children().at(1).children().at(0).text()).toEqual('Last Updated');
      });

      it('renders getDateLabel value', () => {
        expect(wrapper.find('.content').children().at(1).children().at(1).text()).toEqual(wrapper.instance().getDateLabel());
      });
    });

    describe('if props.table does not have last_updated_epoch', () => {
      it('does not render Last Updated section', () => {
        const { props, wrapper } = setup({ table: {
          type: ResourceType.table,
          cluster: '',
          database: '',
          description: 'I am the description',
          key: '',
          last_updated_epoch: null,
          name: 'tableName',
          schema_name: 'tableSchema',
        }});
        expect(wrapper.find('.content').children().at(1).exists()).toBeFalsy();
      });
    });
  });

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
      expect(wrapper.instance().getLink()).toEqual(`/table_detail/${table.cluster}/${table.database}/${table.schema_name}/${table.name}?index=${logging.index}&source=${logging.source}`);
    });
  });
});
