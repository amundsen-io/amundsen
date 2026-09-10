// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import React from 'react';

import StorySection from '../StorySection';
import Table from '.';
import TestDataBuilder from './testDataBuilder';

const dataBuilder = new TestDataBuilder();
const { columns, data } = dataBuilder.build();
const { columns: alignedColumns, data: alignedData } = dataBuilder
  .withAlignedColumns()
  .build();
const { columns: differentWidthColumns } = dataBuilder
  .withFixedWidthColumns()
  .build();
const { columns: fourColumns, data: fourColData } = dataBuilder
  .withFourColumns()
  .build();
const { columns: customColumns, data: customColumnsData } = dataBuilder
  .withOneComponentColumn()
  .build();
const { columns: multipleCustomColumns, data: multipleCustomComlumnsData } =
  dataBuilder.withMultipleComponentsColumn().build();
const { columns: columnsWithAction, data: dataWithAction } = dataBuilder
  .withActionCell()
  .build();
const { columns: columnsWithCollapsedRow, data: dataWithCollapsedRow } =
  dataBuilder.withCollapsedRow().build();

export const TableStates = () => (
  <>
    <StorySection title="Basic Table">
      <Table columns={columns} data={data} />
    </StorySection>
    <StorySection title="Empty Table">
      <Table columns={columns} data={[]} />
    </StorySection>
    <StorySection title="Loading Table">
      <Table columns={[]} data={[]} options={{ isLoading: true }} />
    </StorySection>
  </>
);

export const StyledTable = () => (
  <>
    <StorySection title="with different column alignment">
      <Table columns={alignedColumns} data={alignedData} />
    </StorySection>
    <StorySection title="with 50px row height">
      <Table columns={columns} data={data} options={{ rowHeight: 50 }} />
    </StorySection>
    <StorySection title="with different column widths">
      <Table
        columns={differentWidthColumns}
        data={data}
        options={{ rowHeight: 50 }}
      />
    </StorySection>
    <StorySection title="with four columns">
      <Table
        columns={fourColumns}
        data={fourColData}
        options={{ rowHeight: 50 }}
      />
    </StorySection>
  </>
);

export const CustomizedTable = () => (
  <>
    <StorySection title="with custom column components">
      <Table
        columns={customColumns}
        data={customColumnsData}
        options={{ rowHeight: 40 }}
      />
    </StorySection>
    <StorySection title="with multiple custom column components">
      <Table
        columns={multipleCustomColumns}
        data={multipleCustomComlumnsData}
        options={{ rowHeight: 40 }}
      />
    </StorySection>
    <StorySection title="with Bootstrap dropdown as component">
      <Table
        columns={columnsWithAction}
        data={dataWithAction}
        options={{ rowHeight: 40 }}
      />
    </StorySection>
    <StorySection title="with Custom Empty Message">
      <Table
        columns={columns}
        data={[]}
        options={{
          emptyMessage: 'Custom Empty Message Here!',
        }}
      />
    </StorySection>
  </>
);

export const CollapsibleTable = () => (
  <>
    <StorySection title="with Collapsed Rows">
      <Table
        columns={columnsWithCollapsedRow}
        data={dataWithCollapsedRow}
        options={{
          rowHeight: 40,
        }}
      />
    </StorySection>
    <StorySection
      title="with onExpand handler"
      text="You can open the console to see the handler being called"
    >
      <Table
        columns={columnsWithCollapsedRow}
        data={dataWithCollapsedRow}
        options={{
          rowHeight: 40,
          onExpand: (rowValues, index) => {
            console.log('Expanded row values:', rowValues);
            console.log('Expanded row index:', index);
          },
        }}
      />
    </StorySection>
    <StorySection
      title="with onCollapse handler"
      text="You can open the console to see the handler being called"
    >
      <Table
        columns={columnsWithCollapsedRow}
        data={dataWithCollapsedRow}
        options={{
          rowHeight: 40,
          onCollapse: (rowValues, index) => {
            console.log('Collapsed row values:', rowValues);
            console.log('Collapsed row index:', index);
          },
        }}
      />
    </StorySection>
  </>
);

export default {
  title: 'Components/Table',
  component: Table,
};
