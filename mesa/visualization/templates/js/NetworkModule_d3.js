const NetworkModule = function (svg_width, svg_height) {
  // Create the svg element:
  const svg = d3.create("svg");
  svg
    .attr("class", "NetworkModule_d3")
    .attr("width", svg_width)
    .attr("height", svg_height)
    .style("border", "1px dotted");

  // Append svg to #elements:
  document.getElementById("elements").appendChild(svg.node());

  const width = +svg.attr("width");
  const height = +svg.attr("height");
  const g = svg
    .append("g")
    .classed("network_root", true);

  const tooltip = d3
    .select("body")
    .append("div")
    .attr("class", "d3tooltip")
    .style("opacity", 0);

  const zoom = d3.zoom()
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    });

  svg.call(zoom);

  svg.call(
    zoom.transform,
    d3.zoomIdentity.translate(width / 2, height / 2)
  );

  const links = g.append("g").attr("class", "links");

  const nodes = g.append("g").attr("class", "nodes");

  this.render = (data) => {
    const graph = JSON.parse(JSON.stringify(data));

    const simulation = d3
      .forceSimulation()
      .nodes(graph.nodes)
      .force("charge", d3.forceManyBody().strength(-80).distanceMin(2))
      .force("link", d3.forceLink(graph.edges))
      .force("center", d3.forceCenter())
      .stop();

    for (
      let i = 0,
        n = Math.ceil(
          Math.log(simulation.alphaMin()) /
            Math.log(1 - simulation.alphaDecay())
        );
      i < n;
      ++i
    ) {
      simulation.tick();
    }

    links.selectAll("line").data(graph.edges).enter().append("line");

    links
      .selectAll("line")
      .data(graph.edges)
      .attr("x1", function (d) {
        return d.source.x;
      })
      .attr("y1", function (d) {
        return d.source.y;
      })
      .attr("x2", function (d) {
        return d.target.x;
      })
      .attr("y2", function (d) {
        return d.target.y;
      })
      .attr("stroke-width", function (d) {
        return d.width;
      })
      .attr("stroke", function (d) {
        return d.color;
      });

    links.selectAll("line").data(graph.edges).exit().remove();

    nodes
      .selectAll("circle")
      .data(graph.nodes)
      .enter()
      .append("circle")
      .on("mouseover", function (event, d) {
        tooltip.transition().duration(200).style("opacity", 0.9);
        tooltip
          .html(d.tooltip)
          .style("left", event.pageX + "px")
          .style("top", event.pageY + "px");
      })
      .on("mouseout", function () {
        tooltip.transition().duration(500).style("opacity", 0);
      });

    nodes
      .selectAll("circle")
      .data(graph.nodes)
      .attr("cx", function (d) {
        return d.x;
      })
      .attr("cy", function (d) {
        return d.y;
      })
      .attr("r", function (d) {
        return d.size;
      })
      .attr("fill", function (d) {
        return d.color;
      });

    nodes.selectAll("circle").data(graph.nodes).exit().remove();
  };

  this.reset = () => {};
};
