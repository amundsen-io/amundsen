// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
/* eslint-disable no-underscore-dangle */

import { LineageItem } from 'interfaces';

import {
  buildEdges,
  buildNodes,
  buildSVG,
  compactLineage,
  decompactLineage,
  hasLineageData,
  generatePath,
  toggler,
} from './chart';

import { TreeLineageItem } from './types';

const item: LineageItem = {
  badges: [],
  cluster: 'cluster',
  database: 'database',
  key: 'table-key',
  level: 0,
  name: 'table',
  parent: null,
  schema: 'schema',
  usage: null,
};

const rootNode = {
  children: undefined,
  data: item as LineageItem & { id?: string; data: TreeLineageItem },
  parent: null,
  x: 100,
  y: 100,
  id: '1',
};

const nodeWithParent = {
  children: undefined,
  data: item as LineageItem & { id?: string; data: TreeLineageItem },
  parent: rootNode,
  x: 100,
  y: 100,
  id: '2',
};

describe('D3 Lineage chart', () => {
  describe('lineageDataPredicate', () => {
    it('Needs only one of upstream/downstream to render', () => {
      expect(
        hasLineageData({ upstream_entities: [], downstream_entities: [] })
      ).toBe(false);
      expect(
        hasLineageData({ upstream_entities: [], downstream_entities: [item] })
      ).toBe(true);
      expect(
        hasLineageData({ upstream_entities: [item], downstream_entities: [] })
      ).toBe(true);
    });
  });

  describe('Lineage compact for tree rendering', () => {
    it('should collapse duplicate nodes with different parents', () => {
      const withMultipleParents: LineageItem[] = [
        item,
        { ...item, key: 'another-parent' },
        { ...item, level: 1, key: 'no-parent-level-1', parent: '' },
        { ...item, key: 'child', parent: 'table-key' },
        { ...item, key: 'child', parent: 'another-parent' },
      ];
      const compacted = compactLineage(withMultipleParents);
      const compactedChild = compacted.find((i) => i.key === 'child');
      const withAddedRootParent = compacted.find(
        (i) => i.key === 'no-parent-level-1'
      );
      expect(compacted).toHaveLength(4);
      expect(compactedChild?._parents).toHaveLength(2);
      expect(withAddedRootParent?.parent).toEqual('table-key');
    });
  });

  describe('Decompacting for edge rendering', () => {
    const withMultipleParents: LineageItem[] = [
      item,
      { ...item, key: 'another-parent' },
      { ...item, key: 'child', parent: 'table-key' },
      { ...item, key: 'child', parent: 'another-parent' },
    ];
    const compacted = compactLineage(withMultipleParents);
    const compactedNodes = compacted.map((i) => ({
      ...i,
      data: { data: { key: i.key, _parents: i._parents } },
      y: 100,
      x: 100,
    }));
    const decompactedNodes = decompactLineage(compactedNodes);
    expect(decompactedNodes).toHaveLength(4);
  });

  describe('toggler callback is fired with correct item', () => {
    it('Click on a root works', () => {
      const clickSpy = jest.fn();
      const onClickRoot = toggler(clickSpy);
      onClickRoot(rootNode, [rootNode, nodeWithParent, rootNode]);
      expect(clickSpy.mock.calls.length).toBe(2);
      expect(clickSpy.mock.calls[0][0]).toBe(rootNode);

      const onClickNode = toggler(clickSpy);
      onClickNode(nodeWithParent, [rootNode, nodeWithParent]);
      expect(clickSpy.mock.calls.length).toBe(2);
      expect(clickSpy.mock.calls[1][0]).toBe(rootNode);
    });
  });

  describe('patch generations connects two coordiantes', () => {
    expect(generatePath({ x: 3, y: 5 }, { x: 1, y: 1 })).toMatch(/C 3 3/);
  });

  describe('building an svg should work', () => {
    const el = document.createElement('div');
    buildSVG(el, { height: 100, width: 100 });
    expect(el.getElementsByTagName('svg').length).toBe(1);
    expect(el.getElementsByTagName('g').length).toBe(1);
  });

  describe('testing builder d3 functions for nodes & edges', () => {
    const el = document.createElement('div');
    const { g } = buildSVG(el, { height: 100, width: 100 });
    const edges = [nodeWithParent];
    const clickSpy = jest.fn();
    const onClickRoot = toggler(clickSpy);

    // Not sure how this could be tested.
    buildEdges(g, rootNode, edges);
    buildNodes(g, rootNode, edges, onClickRoot);
  });
});
