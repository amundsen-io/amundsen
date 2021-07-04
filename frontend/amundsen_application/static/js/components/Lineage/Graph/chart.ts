/* eslint-disable no-underscore-dangle, no-param-reassign */

import {
  hierarchy,
  stratify as d3Stratify,
  tree as d3Tree,
} from 'd3-hierarchy';
import { zoom as d3Zoom, zoomIdentity } from 'd3-zoom';
import { select, Selection } from 'd3-selection';
import { Lineage, LineageItem } from 'interfaces';
import {
  ANIMATION_DURATION,
  CHART_DEFAULT_DIMENSIONS,
  CHART_DEFAULT_LABELS,
  LINEAGE_SCENE_MARGIN,
  NODE_STATUS_Y_OFFSET,
  NODE_LABEL_Y_OFFSET,
  UPSTREAM_LABEL_OFFSET,
} from './constants';
import { Coordinates, Dimensions, Labels, TreeLineageNode } from './types';

export interface LineageChartData {
  lineage: Lineage;
  dimensions: Dimensions;
  labels: Labels;
}

export interface LineageChart {
  (selection: any): any;
}

/**
 * Generate a cartesian path between two nodes.
 */
export const generatePath = (src: Coordinates, dst: Coordinates) =>
  // Multiline return for ease of reading
  `M ${src.y} ${src.x}
          C ${(src.y + dst.y) / 2} ${src.x},
            ${(src.y + dst.y) / 2} ${dst.x},
            ${dst.y} ${dst.x}`;
/**
 * Render the upstream/downstream labels on the lineage graph
 */
const renderLabels = (
  svg: Selection<SVGSVGElement, any, null, any>,
  dimensions: Dimensions,
  labels: Labels
) => {
  svg
    .append('foreignObject')
    // @ts-ignore
    .attr('class', 'graph-direction-label  upstream-label')
    .attr(
      'transform',
      `translate(${
        dimensions.width / 2 -
        UPSTREAM_LABEL_OFFSET -
        LINEAGE_SCENE_MARGIN.right
      }, ${LINEAGE_SCENE_MARGIN.top})`
    )
    .html(labels.upstream);

  svg
    .append('foreignObject')
    // @ts-ignore
    .attr('class', 'graph-direction-label downstream-label')
    .attr(
      'transform',
      `translate(${dimensions.width / 2 + LINEAGE_SCENE_MARGIN.left}, ${
        LINEAGE_SCENE_MARGIN.top
      })`
    )
    .html(labels.downstream);
};

/**
 * The d3 Hierarchy module renders single parent relationships only.
 * we compact the lineage to merge duplicate nodes before rendering.
 */
export const compactLineage = (
  items: LineageItem[]
): (LineageItem & { _parents: string[] })[] => {
  const rootNode = items.find((n) => n.level === 0);
  return Object.values(
    items.reduce((acc, n) => {
      if (n.level === 1 && !n.parent && rootNode) {
        n.parent = rootNode.key;
      }

      if (acc.hasOwnProperty(n.key)) {
        acc[n.key]._parents.push(n.parent);
      } else {
        acc[n.key] = n;
        acc[n.key]._parents = [n.parent];
      }
      return acc;
    }, {})
  );
};

/**
 * Allows us to unfurl the list of relationships post stratify-ing, so we can
 * still build the custom edges for multiple parents.
 */
export const decompactLineage = (nodes): TreeLineageNode[] =>
  nodes.reduce((acc, n) => {
    if (n.data.data._parents && n.data.data._parents.length > 1) {
      const parents = nodes.filter((p: TreeLineageNode) =>
        n.data.data._parents.includes(p.data.data.key)
      );

      const newX = parents.reduce((sum, p) => sum + p.x, 0) / parents.length;

      acc = acc.concat(
        parents.map((p) => {
          if (!p.children && !p._children) {
            p.children = [n];
          }

          return {
            ...n,
            x: newX,
            parent: p,
          };
        })
      );
    } else {
      acc.push(n);
    }
    return acc;
  }, [] as TreeLineageNode[]);

/**
 * Render all edges between connected nodes and seed animations.
 */
export const buildEdges = (g, targetNode, nodes) => {
  const treeSelection = g
    .selectAll('path.graph-link')
    .data(nodes, (d: TreeLineageNode) => d.id);

  // Enter any new links at the parent's previous position.
  const edgeEnter = treeSelection
    .enter()
    .insert('path', 'g')
    .attr('class', 'graph-link')
    .attr('d', () => {
      const o = { x: targetNode.x0 || 0, y: targetNode.y0 || 0 };
      return generatePath(o, o);
    });

  // Render connection
  edgeEnter
    .merge(treeSelection)
    .transition()
    .duration(ANIMATION_DURATION)
    .attr('d', (d) => generatePath(d, d.parent));

  // Render multiparent connections
  // Transition out on exit.
  treeSelection
    .exit()
    .transition()
    .duration(ANIMATION_DURATION)
    .attr('d', () => {
      const o = { x: targetNode.x, y: targetNode.y };
      return generatePath(o, o);
    })
    .remove();
};

/**
 * Render all nodes and setup transitions as required
 */
export const buildNodes = (g, targetNode, nodes, onClick) => {
  let uniqueIdSequence = 0;

  const nodeSelection = g
    .selectAll('g.graph-node')
    // eslint-disable-next-line no-return-assign
    .data(nodes, (d) => {
      if (!d.id) {
        uniqueIdSequence += 1;
        d.id = uniqueIdSequence;
      }
      return d.id;
    });

  // Toggle children on click.
  // Enter any new modes at the parent's previous position.
  const nodeEnter = nodeSelection
    .enter()
    .append('g')
    .attr('class', 'graph-node')
    .attr('transform', () => `translate(${targetNode.y0},${targetNode.x0})`)
    .on('click', (_, clicked) => onClick(clicked, nodes));

  // Draw circle around the nodes
  nodeEnter.append('circle').attr('class', 'graph-node').attr('r', 0);

  // Position node label
  nodeEnter
    .append('text')
    .attr('dy', NODE_LABEL_Y_OFFSET)
    .attr('text-anchor', 'middle')
    .text((d, idx) => (idx !== 0 && d.data.data.name ? d.data.data.name : ''));

  // Position visual state for for fold/unfold
  nodeEnter
    .append('text')
    .attr('dy', NODE_STATUS_Y_OFFSET)
    .attr('class', 'plus')
    .attr('text-anchor', 'middle');

  const nodeUpdate = nodeEnter.merge(nodeSelection);

  // Transition to the proper position for the node
  nodeUpdate
    .transition()
    .duration(ANIMATION_DURATION)
    .attr('transform', (d) => {
      // DO NOT UPDATE THE POSITION OF ROOT NODE
      if (d.parent === null) {
        d.y = targetNode.y0;
        d.x = targetNode.x0;
      }
      return 'translate(' + d.y + ',' + d.x + ')';
    });

  // Update the node attributes and style
  nodeUpdate
    .select('circle.graph-node')
    .attr('r', (d) => (d.depth === 0 ? 12 : 8))
    .attr('cursor', 'pointer');

  nodeUpdate.select('text.plus').text((n: TreeLineageNode) => {
    let nodeActionLabel = '';
    if (n.children) {
      nodeActionLabel = '-';
    } else if (n._children) {
      nodeActionLabel = '+';
    }
    return nodeActionLabel;
  });

  // Remove any exiting nodes
  const nodeExit = nodeSelection
    .exit()
    .transition()
    .duration(ANIMATION_DURATION)
    .attr('transform', () => `translate(${targetNode.y},${targetNode.x})`)
    .remove();

  // On exit reduce the node circles size to 0
  nodeExit.select('circle').attr('r', 1e-6);

  // On exit reduce the opacity of text labels
  nodeExit.select('text').style('fill-opacity', 1e-6);
};

/**
 * Create a toggler function with a render callback
 */
export const toggler = (renderer) => (target, nodes) => {
  let roots = nodes.filter((n) => n.parent === null);
  let toUpdate: TreeLineageNode[] = [];
  if (target.parent) {
    if (target.children || target._children) {
      toUpdate = [
        target,
        ...nodes.filter((n) => {
          const targetChildren = target.children || target._children || [];
          const children = n.children || n._children || [];

          return (
            target.id !== n.id &&
            children &&
            children.some((c) =>
              targetChildren.find((tc) => c.data.id === tc.data.id)
            )
          );
        }),
      ];
    } else {
      roots = [];
    }
  } else {
    toUpdate = roots;
  }

  toUpdate.map((n: TreeLineageNode) => {
    if (n.children) {
      n._children = n.children;
      n.children = undefined;
    } else {
      n.children = n._children;
      n._children = undefined;
    }
    return false;
  });

  return roots.map((r) => renderer(r));
};

/**
 * Confirm presence of nodes to render.
 */
export const hasLineageData = (lineage: Lineage) =>
  lineage.downstream_entities.length > 0 ||
  lineage.upstream_entities.length > 0;

/**
 * Builds an svg out of an element
 */
export const buildSVG = (el: HTMLElement, dimensions: Dimensions) => {
  const svg = select(el)
    .append('svg')
    .classed('svg-content', true)
    .attr('width', dimensions.width)
    .attr('height', dimensions.height);

  const g = svg
    .append('g')
    .attr('transform', `translate(${dimensions.width / 2})`);
  return { svg, g };
};

const lc = (): LineageChart => {
  let svg: Selection<SVGSVGElement, any, null, any>;
  let g;

  let dimensions: Dimensions = CHART_DEFAULT_DIMENSIONS;
  let labels: Labels = CHART_DEFAULT_LABELS;
  let lineage: Lineage;

  function renderGraph() {
    const stratify = d3Stratify()
      .id((d: TreeLineageNode) => d.key)
      .parentId((d: any) => d.parent);

    const treemap = d3Tree().size([
      dimensions.height,
      (dimensions.width -
        (LINEAGE_SCENE_MARGIN.left + LINEAGE_SCENE_MARGIN.right)) /
        2,
    ]);

    const upstreamRoot =
      lineage.upstream_entities.length > 0
        ? hierarchy(stratify(lineage.upstream_entities), (d) => d.children)
        : null;

    const downstreamRoot =
      lineage.downstream_entities.length > 0
        ? hierarchy(stratify(lineage.downstream_entities), (d) => d.children)
        : null;

    const zoom = d3Zoom().on('zoom', (e) => {
      const { transform } = e;
      // By default make sure to place the graph in center
      if (!e.sourceEvent) transform.x = dimensions.width / 2;
      g.attr('transform', transform);
      // This is awkward, defined as css/js var.
      g.style('stroke-width', 3 / Math.sqrt(transform.k));
    });

    svg.call(zoom).call(zoom.transform, zoomIdentity);

    function renderRelativeTo(targetPosition: TreeLineageNode) {
      // Transpose upstream over Y axis

      const upstreamNodes = upstreamRoot
        ? treemap(upstreamRoot)
            .descendants()
            .map((c) => {
              c.y *= -1;
              return c;
            })
        : [];

      const downstreamNodes = downstreamRoot
        ? treemap(downstreamRoot).descendants()
        : [];

      const nodes = upstreamNodes.concat(downstreamNodes).map(
        (n: TreeLineageNode): TreeLineageNode => {
          n.x0 = n.x;
          n.y0 = n.y;
          return n;
        }
      );

      const dagNodes = decompactLineage(nodes as TreeLineageNode[]);
      buildNodes(g, targetPosition, dagNodes, toggler(renderRelativeTo));
      buildEdges(
        g,
        targetPosition,
        dagNodes.filter((n) => n.depth !== 0)
      );
    }

    renderRelativeTo({
      x0: dimensions.height / 2,
      y0: 0,
    } as TreeLineageNode);
  }

  const chart = ((
    _selection: Selection<HTMLElement, LineageChartData, any, any>
  ) => {
    _selection.each(function bc(_data: LineageChartData) {
      ({ dimensions, labels, lineage } = _data);

      if (!svg) {
        ({ svg, g } = buildSVG(this, dimensions));
      }

      renderLabels(svg, dimensions, labels);

      if (hasLineageData(lineage)) {
        lineage = {
          upstream_entities: compactLineage(lineage.upstream_entities),
          downstream_entities: compactLineage(lineage.downstream_entities),
        };
        renderGraph();
      }
    });
  }) as LineageChart;

  return chart;
};

export default lc;
