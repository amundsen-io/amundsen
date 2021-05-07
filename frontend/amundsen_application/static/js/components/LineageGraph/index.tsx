// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

/* eslint-disable no-underscore-dangle, no-param-reassign */

import * as d3 from 'd3';
import * as React from 'react';

import { Lineage } from 'interfaces';

import './styles.scss';

import { LeftIcon } from 'components/SVGIcons';

export interface LineageGraphProps {
  lineage: Lineage;
}

interface LineageGraphState {}

export class LineageGraph extends React.Component<
  LineageGraphProps,
  LineageGraphState
> {
  state: any = {};

  private nodeRef = React.createRef<HTMLDivElement>();

  drawTree = this._drawTree.bind(this);

  componentDidMount() {
    // Centering the graph
    const dimensions = this.nodeRef.current!.getBoundingClientRect();
    if (this.nodeRef.current) {
      // const dimensions = this.nodeRef.current!.getBoundingClientRect();
      this.setState({
        nodeTranslate: {
          x: dimensions.width / 2,
          y: dimensions.height / 2,
        },
      });
    }

    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    // Setting up the dimensions/fallback dimensions
    const totalWidth = dimensions.width || 1280 - (margin.left + margin.right);
    const totalHeight =
      dimensions.height || 1024 - (margin.top + margin.bottom);

    const svgContainer = d3
      .select(this.nodeRef.current)
      .append('svg')
      .attr('class', 'svg-container')
      .attr('viewBox', [0, 0, totalWidth, totalHeight]);

    svgContainer
      .append('foreignObject')
      .attr('class', 'direction-label  upstream-label')
      .attr(
        'transform',
        `translate(${totalWidth / 2 - 150 - margin.right}, ${margin.top})`
      )
      .html('<img class="icon icon-left-arrow" /> Upstream');

    svgContainer
      .append('foreignObject')
      .attr('class', 'direction-label downstream-label')
      .attr(
        'transform',
        `translate(${totalWidth / 2 + margin.left}, ${margin.top})`
      )
      .html('<img class="icon icon-right-arrow" /> downstream');

    this.drawTree(totalWidth / 2, totalHeight, margin);
  }

  _drawTree(width: number, height: number, margin) {
    const { lineage } = this.props;

    const stratify = d3
      .stratify()
      .id((d) => d.key)
      .parentId((d) => d.parent);

    let uniqueIdCounter = 0;
    const animationDuration = 500;

    const treemap = d3.tree().size([height, width / 2]);
    const upstreamRoot = d3.hierarchy(
      stratify(lineage.upstream_entities),
      (d) => d.children
    );
    const downstreamRoot = d3.hierarchy(
      stratify(lineage.downstream_entities),
      (d) => d.children
    );

    const root = {
      x0: height / 2,
      y0: 0,
    };

    const svg = d3
      .select('svg')
      .append('g')
      .attr('transform', `translate(${width})`);

    // Collapse after the second level
    // upstreamRoot.children.forEach(collapse);
    // downstreamRoot.children.forEach(collapse);

    update(root);

    function collapse(d) {
      if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
      }
    }

    function makeUpstream(array) {
      return array.map((item) => {
        item.y *= -1;
        return item;
      });
    }

    function update(source) {
      const upNodes = makeUpstream(treemap(upstreamRoot).descendants());
      const downNodes = treemap(downstreamRoot).descendants();

      const nodes = upNodes.concat(downNodes);
      const links = upNodes.slice(1).concat(downNodes.slice(1));

      // ****************** Nodes
      const node = svg
        .selectAll('g.node')
        // eslint-disable-next-line no-return-assign
        .data(nodes, (d) => d.id || (d.id = ++uniqueIdCounter));

      // Enter any new modes at the parent's previous position.
      const nodeEnter = node
        .enter()
        .append('g')
        .attr('class', 'node')
        .attr('transform', (d) => `translate(${source.y0},${source.x0})`)
        .on('click', (event, d) => click(event, d, nodes));

      // Add Circle for the nodes
      nodeEnter.append('circle').attr('class', 'node').attr('r', 0);
      // .style('fill', (d) => (d._children ? 'lightsteelblue' : '#fff'));

      // Add labels for the nodes
      nodeEnter
        .append('text')
        .attr('dy', '.35em')
        .attr('x', function (d) {
          return d.children || d._children ? -13 : 13;
        })
        .attr('text-anchor', function (d) {
          return d.children || d._children ? 'end' : 'start';
        })
        .text(function (d, index) {
          if (index === 0) return '';
          return `${d.data.data.schema}.${d.data.data.name}`;
        });

      nodeEnter
        .append('text')
        .attr('dx', '-.25em')
        .attr('dy', '.25em')
        .attr('class', 'plus')
        .style('color', '#8b37ff')
        .text((d) => (d._children ? '+' : ''));

      // UPDATE
      const nodeUpdate = nodeEnter.merge(node);

      // Transition to the proper position for the node
      nodeUpdate
        .transition()
        .duration(animationDuration)
        .attr('transform', (d) => {
          // DO NOT UPDATE THE POSITION OF ROOT NODE
          if (d.parent === null) {
            d.y = root.y0;
            d.x = root.x0;
          }
          return 'translate(' + d.y + ',' + d.x + ')';
        });

      // Update the node attributes and style
      nodeUpdate
        .select('circle.node')
        .attr('r', (d) => (d.depth === 0 ? 12 : 8))
        // .style('fill', function (d) {
        //   return d._children ? 'lightsteelblue' : '#fff';
        // })
        .attr('cursor', 'pointer');

      nodeUpdate.select('text.plus').text((d) => (d._children ? '+' : ''));

      // Remove any exiting nodes
      const nodeExit = node
        .exit()
        .transition()
        .duration(animationDuration)
        .attr('transform', (d) => `translate(${source.y},${source.x})`)
        .remove();

      // On exit reduce the node circles size to 0
      nodeExit.select('circle').attr('r', 1e-6);

      // On exit reduce the opacity of text labels
      nodeExit.select('text').style('fill-opacity', 1e-6);

      // ****************** links section ***************************

      // Creates a curved (diagonal) path from parent to the child nodes
      function diagonal(s, d) {
        return `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                  ${(s.y + d.y) / 2} ${d.x},
                  ${d.y} ${d.x}`;
      }

      // Update the links...
      const link = svg.selectAll('path.link').data(links, function (d) {
        return d.id;
      });

      // Enter any new links at the parent's previous position.
      const linkEnter = link
        .enter()
        .insert('path', 'g')
        .attr('class', 'link')
        .attr('d', function (d) {
          const o = { x: source.x0, y: source.y0 };
          return diagonal(o, o);
        });

      // UPDATE
      const linkUpdate = linkEnter.merge(link);

      // Transition back to the parent element position
      linkUpdate
        .transition()
        .duration(animationDuration)
        .attr('d', function (d) {
          return diagonal(d, d.parent);
        });

      // Remove any exiting links
      const linkExit = link
        .exit()
        .transition()
        .duration(animationDuration)
        .attr('d', function (d) {
          const o = { x: source.x, y: source.y };
          return diagonal(o, o);
        })
        .remove();

      // Store the old positions for transition.
      nodes.forEach(function (d) {
        d.x0 = d.x;
        d.y0 = d.y;
      });

      // Toggle children on click.
      function click(event, d, nodes) {
        // If the click is via a parent root, then find
        // both the upstream/downstream roots, and operate
        let itemsToUpdate: any = [];
        if (d.parent) itemsToUpdate = [d];
        else itemsToUpdate = nodes.filter((item) => item.parent === null);

        itemsToUpdate.map((item) => {
          if (item.children) {
            item._children = item.children;
            item.children = null;
          } else {
            item.children = item._children;
            item._children = null;
          }
          update(item);
        });
      }
    }
  }

  render() {
    return (
      <div
        className="lineage-graph"
        ref={this.nodeRef}
        translate={this.state.nodeTranslate}
      />
    );
  }
}

export default LineageGraph;
