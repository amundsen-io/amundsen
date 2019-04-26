import * as React from 'react';

import { shallow } from 'enzyme';

import Avatar from 'react-avatar';
import { Link } from 'react-router-dom';

import TableListItem, { TableListItemProps } from '../';
import { ResourceType } from '../../types';

describe('TableListItem', () => {
    let props: TableListItemProps;
    let subject;

    beforeEach(() => {
        props = {
          logging: { source: 'src', index: 0 },
          table: {
            type: ResourceType.table,
            cluster: '',
            database: '',
            description: 'I am the description',
            key: '',
            last_updated_epoch: null,
            name: 'tableName',
            schema_name: 'tableSchema',
          },
        }
        subject = shallow(<TableListItem {...props} />);
    });

    describe('render', () => {
        it('renders item as Link', () => {
          expect(subject.find(Link).exists()).toBeTruthy();
        });

        it('renders table name', () => {
          expect(subject.find('.content').children().at(0).children().at(0).text()).toEqual('tableSchema.tableName');
        });

        it('renders table description', () => {
          expect(subject.find('.content').children().at(0).children().at(1).text()).toEqual('I am the description');
        });

        it('renders secondary title if table has last_updated_epoch ', () => {
          props.table.last_updated_epoch = 1553829681;
          subject.setProps(props);
          expect(subject.find('.content').children().at(1).children().at(0).text()).toEqual('Last Updated');
        });

        it('renders secondary description w/ getDateLabel value if table has last_updated_epoch ', () => {
          subject.instance().getDateLabel = jest.fn(() => 'Mar 28, 2019')
          props.table.last_updated_epoch = 1553829681;
          subject.setProps(props);
          expect(subject.find('.content').children().at(1).children().at(1).text()).toEqual('Mar 28, 2019');
        });
    });

    describe('getDateLabel', () => {
        it('getDateLabel returns correct string', () => {
          props.table.last_updated_epoch = 1553829681;
          subject.setProps(props);
          /* Note: Jest will convert date to UTC, expect to see different strings for an epoch value in the tests vs UI*/
          expect(subject.instance().getDateLabel()).toEqual('Mar 29, 2019');
        });
    });

    describe('getLink', () => {
        it('getLink returns correct string', () => {
          const { table, logging } = props;
          expect(subject.instance().getLink()).toEqual(`/table_detail/${table.cluster}/${table.database}/${table.schema_name}/${table.name}?index=${logging.index}&source=${logging.source}`);
        });
    });
});
