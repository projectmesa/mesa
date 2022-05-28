"use strict";
//Note: This pie chart is based off the example found here:
//https://bl.ocks.org/mbostock/3887235

const PieChartModule = function (fields, canvas_width, canvas_height) {
  const createElement = (tagName, attrs) => {
    const element = document.createElement(tagName);
    Object.assign(element, attrs);
    return element;
  };

  // Create the overall chart div
  const chartDiv = createElement("div", {
    className: "pie chart",
    width: canvas_width,
  });
  document.getElementById("elements").appendChild(chartDiv);

  // Create the svg element:
  const svg = d3.create("svg");
  svg
    .attr("width", canvas_width)
    .attr("height", canvas_height)
    .style("border", "1px dotted");
  chartDiv.appendChild(svg.node());

  //create the legend
  const legend = d3.create("div");
  legend
    .attr("class", "legend")
    .attr("style", `display:block;width:${canvas_width}px;text-align:center`);
  chartDiv.appendChild(legend.node());

  legend
    .selectAll("span")
    .data(fields)
    .enter()
    .append("span")
    .html(function (d) {
      return (
        "<span style='color:" +
        d["Color"] +
        ";'> &#11044;</span>" +
        "&nbsp;" +
        d["Label"].replace(" ", "&nbsp;")
      );
    })
    .attr("style", "padding-left:10px;padding-right:10px;");

  // setup the d3 svg selection
  const width = +svg.attr("width");
  const height = +svg.attr("height");
  const maxRadius = Math.min(width, height) / 2;
  const g = svg
    .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  // Create the base chart and helper methods
  const color = d3.scaleOrdinal(fields.map((field) => field["Color"]));
  const pie = d3
    .pie()
    .sort(null)
    .value(function (d) {
      return d;
    });
  const path = d3.arc().outerRadius(maxRadius).innerRadius(0);
  const arc = g
    .selectAll(".arc")
    .data(pie(fields.map((field) => 0))) //Initialize the pie chart with dummy data
    .enter()
    .append("g")
    .attr("class", "arc");

  arc
    .append("path")
    .attr("d", path)
    .style("fill", function (d, i) {
      return color(i);
    })
    .append("title")
    .text(function (d) {
      return d.value;
    });

  this.render = function (data) {
    //Update the pie chart each time new data comes in
    arc
      .data(pie(data))
      .select("path")
      .attr("d", path)
      .select("title")
      .text(function (d) {
        return (
          d.value +
          " : " +
          (((d.endAngle - d.startAngle) * 100.0) / (Math.PI * 2)).toFixed(2) +
          "%"
        );
      });
  };

  this.reset = function () {
    //Reset the chart by setting each field to 0
    arc
      .data(pie(fields.map((field) => 0)))
      .enter()
      .select("g");

    arc.select("path").attr("d", path);
  };
};
