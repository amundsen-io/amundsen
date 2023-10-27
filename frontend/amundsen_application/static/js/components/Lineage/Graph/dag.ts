/* eslint-disable no-underscore-dangle, no-param-reassign */
import { select, Selection } from 'd3-selection';
import * as d3 from 'd3';
import { drag } from 'd3-drag';
import { zoom } from 'd3-zoom';
import { SimulationNodeDatum } from 'd3-force';

import { Lineage, LineageItem } from 'interfaces';
import {
  ANIMATION_DURATION,
  CHART_DEFAULT_DIMENSIONS,
  CHART_DEFAULT_LABELS,
  LINEAGE_SCENE_MARGIN,
  NODE_STATUS_Y_OFFSET,
  NODE_LABEL_X_OFFSET,
  NODE_LABEL_Y_OFFSET,
  UPSTREAM_LABEL_OFFSET,
} from './constants';
import { Coordinates, Dimensions, Labels, TreeLineageNode } from './types';
import { getLink } from 'components/ResourceListItem/TableListItem';

interface D3LineageItem extends LineageItem {
  direction?: string | 'upstream' | 'downstream' | 'root';
  x?: number;
  y?: number;
  fx?: number|null;
  fy?: number|null;
}

export interface LineageChartData {
  lineage: Lineage;
  dimensions: Dimensions;
  labels: Labels;
}

export interface LineageChart {
  (selection: any): any;
}

/**
 * Confirm presence of nodes to render.
 */
export const hasLineageData = (lineage: Lineage) =>
  lineage.downstream_entities.length > 0 ||
  lineage.upstream_entities.length > 0;

/**
 * Returns the link to the table
 */
const getTableDetailLink = (d) =>
  `/table_detail/${d.cluster}/${d.database}/${d.schema}/${d.name}`

const getSearchLink = (d) =>
  `/search?resource=table&index=0&filters=${encodeURIComponent(`{"schema":{"value":"${d.schema}"},"cluster":{"value":"${d.cluster}"}}`)}`;
  // https://wilcox.cmdrvl.com/search?resource=table&index=0&filters=%7B%22schema%22%3A%7B%22value%22%3A%22staging_wilcox%22%7D%2C%22database%22%3A%7B%22value%22%3A%22Snowflake%22%7D%7D

function toD3LineageItem(item: LineageItem): D3LineageItem {
  return {
    ...item
    // You can add any default fx, fy values if needed here.
  };
}

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

const chart: LineageChart = function(selection: Selection<HTMLElement, LineageChartData, any, any>) {
  selection.each(function(data) {
      const { lineage, dimensions, labels } = data;

      const el = this;

      const width = dimensions.width - (LINEAGE_SCENE_MARGIN.left + LINEAGE_SCENE_MARGIN.right);
      const height = dimensions.height - (LINEAGE_SCENE_MARGIN.top + LINEAGE_SCENE_MARGIN.bottom);
      // const width = dimensions.width;
      // const height = dimensions.height;

      const svg = select(el).append('svg')
          .attr('width', width)
          .attr('height', height)
          .attr('viewBox', `0 0 ${width} ${height}`)
          .attr('preserveAspectRatio', 'xMidYMid meet');

      // renderLabels(svg, dimensions, labels);

      if (hasLineageData(lineage)) {
        const levelGap = 150; // Gap between levels vertically. Adjust as needed.
        const nodeGap = 200;  // Gap between nodes in the same level. Adjust as needed.
        const nodeRectWidth = 250;  // Increased width
        const nodeRectHeight = 50;
        const textMargin = 10; // Margin for the text inside the rectangle

        // Process lineage data for D3
        const nodesMap = new Map<string, D3LineageItem>();

        lineage.upstream_entities.forEach(item => {
            if (!nodesMap.has(item.key)) {
                let directionVal = 'upstream';
                if (item.level === 0) {
                    directionVal = 'root';
                }
                nodesMap.set(item.key, { ...toD3LineageItem(item), direction: directionVal });
            }
        });

        lineage.downstream_entities.forEach(item => {
            if (!nodesMap.has(item.key)) {
                let directionVal = 'upstream';
                if (item.level === 0) {
                    directionVal = 'root';
                }
                nodesMap.set(item.key, { ...toD3LineageItem(item), direction: directionVal });
            }
        });

        const nodes = Array.from(nodesMap.values());
        const rootNode = nodes.find(node => node.level === 0);

        if (!rootNode) {
          throw new Error("Root node not found");
        }

        const rootX = width / 2 - (nodeRectWidth*2);
        const rootY = height / 2 - (nodeRectHeight*2);

        rootNode.fx = rootX;
        rootNode.fy = rootY;

        // nodes.forEach(node => {
        //     const yPosition = rootY + (node.level * levelGap);
        //     const xPosition = rootX + (node.level * nodeGap);
        //     node.x = xPosition;
        //     node.y = yPosition;
        //     node.fy = node.y;  // Fixing the y-coordinate for each node
        // });

        // Upstream/Downstream Top/Bottom
        // nodes.forEach(node => {
        //     let yPosition;
        //     if (node.direction === 'upstream') {
        //         yPosition = rootY - (node.level * levelGap);
        //     } else if (node.direction === 'downstream') {
        //         yPosition = rootY + (node.level * levelGap);
        //     } else {
        //         yPosition = rootY;  // For the rootNode itself
        //     }
        //     const xPosition = rootX + (node.level * nodeGap);
        //     node.x = xPosition;
        //     node.y = yPosition;
        //     node.fy = node.y;  // Fixing the y-coordinate for each node
        // });

        // Upstream/Downstream Left/Right
        nodes.forEach(node => {
            let yPosition;
            let xPosition;

            if (node.direction === 'upstream') {
                yPosition = rootY - (node.level * levelGap);
                xPosition = rootX - (node.level * nodeGap);  // Move left for upstream
            } else if (node.direction === 'downstream') {
                yPosition = rootY + (node.level * levelGap);
                xPosition = rootX + (node.level * nodeGap);  // Move right for downstream
            } else {
                yPosition = rootY;  // For the rootNode itself
                xPosition = rootX;  // rootNode stays centered
            }

            node.x = xPosition;
            node.y = yPosition;
            node.fy = node.y;  // Fixing the y-coordinate for each node
        });

        type Link = { source: string; target: string; direction: 'upstream' | 'downstream' };

        const links: Link[] = [];

        // Building Links for upstream_entities
        lineage.upstream_entities.forEach(item => {
            if (item.parent) {
                // links.push({ source: item.parent, target: item.key, direction: 'upstream' });
                links.push({ source: item.key, target: item.parent, direction: 'upstream' });
            }
        });

        // Building Links for downstream_entities
        lineage.downstream_entities.forEach(item => {
            if (item.parent) {
                links.push({ source: item.parent, target: item.key, direction: 'downstream' });
                // links.push({ source: item.key, target: item.parent, direction: 'downstream' });
            }
        });

        // Arrow
        svg.append('defs').append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0, 0, 4, 4')
            .attr('refX', 2)
            .attr('refY', 2)
            .attr('markerWidth', 4)
            .attr('markerHeight', 4)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,0 L4,2 L0,4')
            .attr('stroke', 'black')
            .attr('fill', 'black');

        const collisionRadius = Math.sqrt((nodeRectWidth * nodeRectWidth) + (nodeRectHeight * nodeRectHeight)) / 2;

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id((d: SimulationNodeDatum) => (d as D3LineageItem).key))
            .force("charge", d3.forceManyBody().strength(-500))  // Change the value from -200 to a larger negative number
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide(collisionRadius));

        const initialScale = 0.8; // Adjust as needed
        const initialTranslate = [(width - rootNode.fx) / 2, (height - rootNode.fy) / 2]; // Center around rootNode

        // const g = svg.append('g');
        const g = svg.append('g')
            .attr('transform', `translate(${initialTranslate}) scale(${initialScale})`);

        // Arrow for the end of the link
        svg.append('defs').append('marker')
            .attr('id', 'arrow-end')

        // Arrow for the middle of the link
        svg.append('defs').append('marker')
            .attr('id', 'arrow-mid')
            .attr('viewBox', '0, 0, 4, 4')
            .attr('refX', 2)
            .attr('refY', 2)
            .attr('markerWidth', 4)
            .attr('markerHeight', 4)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,0 L4,2 L0,4')
            .attr('stroke', 'black')
            .attr('fill', 'black');

        const link = g.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("path")
            .data(links)
            .join("path")
            .attr("stroke-width", 4)
            .attr('marker-end', 'url(#arrow-end)')
            .attr('marker-mid', 'url(#arrow-mid)'); // add this line

        const nodeGroup = g.append("g")
            .selectAll("g")
            .data(nodes)
            .enter().append("g")
            .attr("transform", d => `translate(${d.x}, ${d.y})`)
            .call(drag<SVGGElement, D3LineageItem>()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Adding the anchor element
        // const nodeTableDetailsAnchor = nodeGroup.append("a")
        //     .attr("xlink:href", function(d){ return getTableDetailLink(d) })
            // .attr("target", "_blank"); // Opens link in new tab

        // const nodeSearchAnchor = nodeGroup.append("a")
        //     .attr("xlink:href", function(d){ return getSearchLink(d) })
            // .attr("target", "_blank"); // Opens link in new tab

        // const nodeRect = nodeTableDetailsAnchor.append("rect")
        const nodeRect = nodeGroup.append("rect")
            .attr("rx", 5) // rounded corners
            .attr("ry", 5)
            .attr("width", nodeRectWidth)  // adjust dimensions
            .attr("height", nodeRectHeight)
            .attr("fill", d => d.key === rootNode.key ? "black" : "#DEFF2D")
            .attr("stroke", d => d.key === rootNode.key ? "#DEFF2D" : "black")
            .attr("stroke-width", 2);

        const nodeLabel = nodeGroup.append("text")
            .attr("text-anchor", "start") // This left-aligns the text
            .style("dominant-baseline", "hanging")
            .style("fill", d => d.key === rootNode.key ? "#DEFF2D" : "black")
            .style("stroke", d => d.key === rootNode.key ? "#DEFF2D" : "black");

        nodeLabel.append("a")
            .attr("xlink:href", function(d){ return getSearchLink(d) })
            .append("tspan")
            .attr("x", textMargin)
            .attr("dy", "10")
            .style("fill", d => d.key === rootNode.key ? "#DEFF2D" : "black")
            .style("stroke", d => d.key === rootNode.key ? "#DEFF2D" : "black")
            .text((d: D3LineageItem) => `${d.cluster}.${d.schema}`)
            .each(function() {
                truncateText(select(this), nodeRectWidth - 2 * textMargin);
            });

        nodeLabel.append("a")
            .attr("xlink:href", function(d){ return getTableDetailLink(d) }).append("tspan")
            .attr("x", textMargin)
            .attr("dy", "20")
            .style("font-weight", "bold") // Making the name bold
            .style("font-size", "18px") // Larger font size
            .style("fill", d => d.key === rootNode.key ? "#DEFF2D" : "black")
            .style("stroke", d => d.key === rootNode.key ? "#DEFF2D" : "black")
            .text((d: D3LineageItem) => d.name)
            .each(function() {
                truncateText(select(this), nodeRectWidth - 2 * textMargin);
            });

        const clip = svg.append("defs").append("clipPath")
            .attr("id", "clip-rect")
            .append("rect")
            .attr("width", nodeRectWidth)  // Just use full width here to test
            .attr("height", nodeRectHeight);  // Using full height to test
        nodeLabel.attr("clip-path", "url(#clip-rect)");

        const nodeTitle = nodeGroup.append("title").text((d: D3LineageItem) => `${d.cluster}.${d.schema}.${d.name}`);

        // simulation.on("tick", () => {
        //     link
        //         .attr("x1", (d: any) => d.source.x)
        //         .attr("y1", (d: any) => d.source.y)
        //         .attr("x2", (d: any) => d.target.x)
        //         .attr("y2", (d: any) => d.target.y);

        //     nodeGroup.attr("transform", d => `translate(${d.x}, ${d.y})`);
        // });

        simulation.on("tick", () => {
            link.attr("d", (d: any) => {
                const sourceX = d.source.x + nodeRectWidth / 2;
                const sourceY = d.source.y + nodeRectHeight / 2;
                const targetX = d.target.x + nodeRectWidth / 2;
                const targetY = d.target.y + nodeRectHeight / 2;

                // Calculate intermediate points
                const t1 = 0.25;
                const t2 = 0.50;
                const t3 = 0.75;
                const x1 = lerp(sourceX, targetX, t1);
                const y1 = lerp(sourceY, targetY, t1);
                const x2 = lerp(sourceX, targetX, t2);
                const y2 = lerp(sourceY, targetY, t2);
                const x3 = lerp(sourceX, targetX, t3);
                const y3 = lerp(sourceY, targetY, t3);

                return `M ${sourceX} ${sourceY}
                        L ${x1} ${y1}
                        L ${x2} ${y2}
                        L ${x3} ${y3}
                        L ${targetX} ${targetY}`;
            });

            nodeGroup.attr("transform", d => `translate(${d.x}, ${d.y})`);

        });


        // for (let i = 0; i < 100; ++i) simulation.tick();

        const zoomBehavior = zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });

        svg.call(zoomBehavior)
            .call(zoomBehavior.transform, d3.zoomIdentity.translate(initialTranslate[0], initialTranslate[1]).scale(initialScale));

        function dragstarted(event, d: D3LineageItem) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d: D3LineageItem) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d: D3LineageItem) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = d.x;  // Set the fixed x and y to the current position
            d.fy = d.y;
        }

        function truncateText(textSelection, maxWidth) {
            let textLength = textSelection.node().getComputedTextLength();
            let textContent = textSelection.text();

            while (textLength > maxWidth && textContent.length > 0) {
                textContent = textContent.slice(0, -1);
                textSelection.text(textContent + '...');
                textLength = textSelection.node().getComputedTextLength();
            }
        }

        // Helper function for linear interpolation
        function lerp(a: number, b: number, t: number) {
            return a + t * (b - a);
        }
      }
  });
};

export default chart;