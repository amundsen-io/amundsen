// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

/* eslint-disable no-underscore-dangle, no-param-reassign */

import * as d3 from 'd3';
import * as React from 'react';

import { Lineage } from 'interfaces';

import './styles.scss';

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

    const up = {
      name: 'root',
      children: [
        {
          name: 'upstream 2',
          position: 'left',
          children: [
            {
              name: 'upstream 4',
              position: 'left',
              children: [
                { name: 'upstream 10', position: 'left', size: 7500 },
                { name: 'upstream 11', position: 'left', size: 12000 },
              ],
            },
            {
              name: 'upstream 5',
              position: 'left',
              children: [
                {
                  name: 'upstream 12',
                  position: 'left',
                  children: [
                    { name: 'upstream 16', position: 'left', size: 10000 },
                    { name: 'upstream 17', position: 'left', size: 12000 },
                  ],
                },
                { name: 'upstream 13', position: 'left', size: 5000 },
              ],
            },
          ],
        },
        {
          name: 'upstream 3',
          position: 'left',
          children: [
            {
              name: 'upstream 6',
              position: 'left',
              children: [
                { name: 'upstream 14', position: 'left', size: 8000 },
                { name: 'upstream 15', position: 'left', size: 9000 },
              ],
            },
            {
              name: 'upstream 7',
              position: 'left',
              children: [
                { name: 'upstream 8', position: 'left', size: 10000 },
                { name: 'upstream 9', position: 'left', size: 12000 },
              ],
            },
          ],
        },
      ],
    };

    const down = {
      name: 'root',
      children: [
        {
          name: 'downstream 2',
          children: [
            {
              name: 'downstream 4',
              children: [
                { name: 'downstream 10', size: 7500 },
                { name: 'downstream 11', size: 12000 },
              ],
            },
            {
              name: 'downstream 5',
              children: [
                {
                  name: 'downstream 12',
                  children: [
                    { name: 'downstream 16', size: 10000 },
                    { name: 'downstream 17', size: 12000 },
                  ],
                },
                { name: 'downstream 13', size: 5000 },
              ],
            },
          ],
        },
        {
          name: 'downstream 7',
          children: [
            { name: 'downstream 8', size: 10000 },
            { name: 'downstream 9', size: 12000 },
          ],
        },
      ],
    };
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    // Setting up the dimensions/fallback dimensions
    const totalWidth = dimensions.width || 1280 - (margin.left + margin.right);
    const totalHeight =
      dimensions.height || 1024 - (margin.top + margin.bottom);

    d3.select(this.nodeRef.current)
      .append('svg')
      .attr('viewBox', [0, 0, totalWidth, totalHeight]);

    this.drawTree({ up, down }, totalWidth / 2, totalHeight, margin);
  }

  drawTree(data: any, width: number, height: number, margin) {
    let uniqueIdCounter = 0;
    const animationDuration = 500;

    const treemap = d3.tree().size([height, width]);
    const upstreamRoot = d3.hierarchy(data.up, (d) => d.children);
    const downstreamRoot = d3.hierarchy(data.down, (d) => d.children);

    const root = {
      x0: height / 2,
      y0: 0,
    };

    const svg = d3
      .select('svg')
      .append('g')
      .attr('transform', `translate(${width + margin.left},${margin.top})`);

    // Collapse after the second level
    upstreamRoot.children.forEach(collapse);
    downstreamRoot.children.forEach(collapse);

    update(root);

    function collapse(d) {
      if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
      }
    }

    function splitArray(array) {
      return array.map((item) => {
        let dr = 1;
        if (item.data && item.data.position && item.data.position === 'left') {
          dr = -1;
        }
        item.y *= dr;
        return item;
      });
    }

    function update(source) {
      const upNodes = treemap(upstreamRoot).descendants();
      const downNodes = treemap(downstreamRoot).descendants();

      const nodes = splitArray(upNodes.concat(downNodes));
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
        .attr('class', 'node fixed')
        .attr('transform', (d) => `translate(${source.y0},${source.x0})`)
        .on('click', (event, d) => click(event, d, nodes));

      // Add Circle for the nodes
      nodeEnter
        .append('circle')
        .attr('class', 'node')
        .attr('r', 0)
        .style('fill', (d) => (d._children ? 'lightsteelblue' : '#fff'));

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
        .text(function (d) {
          return d.name || d.text || d.data.name;
        });

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
        .attr('r', 10)
        .style('fill', function (d) {
          return d._children ? 'lightsteelblue' : '#fff';
        })
        .attr('cursor', 'pointer');

      // Remove any exiting nodes
      const nodeExit = node
        .exit()
        .transition()
        .duration(animationDuration)
        .attr('transform', (d) => {
          return `translate(${source.y},${source.x})`;
        })
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
