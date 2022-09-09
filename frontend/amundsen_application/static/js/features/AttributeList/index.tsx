import * as React from 'react';

import './styles.scss';
import Table, {
    TableColumn as ReusableTableColumn,
} from 'components/Table';
import { EMPTY_MESSAGE } from './constraint';
import { Attribute } from 'interfaces/Attribute';
import ColumnDescEditableText from 'features/ColumnList/ColumnDescEditableText';
import { getMaxLength } from 'config/config-utils';
export interface ComponentProps {
    attributes: Array<Attribute>;
}
export type AttributeListProps = ComponentProps;
type ContentType = {
    title?: string;
};
type FormattedDataType = {
    content: ContentType;
    description?: string;
    index : number
};
const AttributeList: React.FC<AttributeListProps> = ({
    attributes
}: ComponentProps) => {
    let selectedIndex;
    const formattedData: FormattedDataType[] = attributes?.map((item, index) => {
        return {
            content: {
                title: item.name,
            },
            description: item.description,
            index : index
        };
    });
    let formattedColumns: ReusableTableColumn[] = [
        {
            title: 'Name',
            field: 'content',
            component: ({ title }: ContentType) => (
                <>
                    <div className="column-name">{title}</div>
                </>
            ),
        },{
            title: 'Description',
            field: 'description',
            component: (description) => (
                <>
                    <div className="column-desc truncated">{description}</div>
                </>
            ),
        }
    ];
    return (
        <Table
            columns={formattedColumns}
            data={formattedData}
            options={{
                rowHeight: 72,
                emptyMessage: EMPTY_MESSAGE,
                tableClassName: 'table-detail-table',
            }}
        />
    );
};
export default AttributeList;