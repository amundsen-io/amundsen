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
            description: '',
            key: '',
            last_updated_epoch: null,
            name: '',
            schema_name: '',
          },
        }
        subject = shallow(<TableListItem {...props} />);
    });

    describe('render', () => {
        it('renders item as Link', () => {
          expect(subject.find(Link).exists()).toBeTruthy();
        });


        it('renders correct text in main-title', () => {
          const { table } = props;
          expect(subject.find('#main-title').text()).toEqual(`${table.schema_name}.${table.name}`);
        });

        it('renders main-description', () => {
          const { table } = props;
          expect(subject.find('#main-description').text()).toEqual(table.description);
        });

        it('renders secondary-description w/ getDateLabel value if table has last_updated_epoch ', () => {
          subject.instance().getDateLabel = jest.fn(() => 'Mar 28, 2019')
          props.table.last_updated_epoch = 1553829681;
          subject.setProps(props);
          expect(subject.find('#secondary-description').text()).toEqual('Mar 28, 2019');
        });
    });
    describe('getDateLabel', () => {
        it('getDateLabel returns correct string', () => {
          props.table.last_updated_epoch = 1553829681;
          subject.setProps(props);
          /* Note: Jest will convert date to UTC, expect to see different strings for an epoch value in the tests vs UI */
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
