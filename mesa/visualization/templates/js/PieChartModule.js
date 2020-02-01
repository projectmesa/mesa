'use strict';
//Note: This pie chart is based off the example found here:
//https://bl.ocks.org/mbostock/3887235

var PieChartModule = function(fields, canvas_width, canvas_height) {
    // Create the overall chart div
    var chart_div_tag = "<div class='pie chart' width='" + canvas_width + "'></div>";
    var chart_div = $(chart_div_tag)[0];
    $("#elements").append(chart_div);

    // Create the tag:
    var svg_tag = "<svg width='" + canvas_width + "' height='" + canvas_height + "' ";
    svg_tag += "style='border:1px dotted'></svg>";
    // Append it to #elements
    var svg_element = $(svg_tag)[0];
    chart_div.append(svg_element);

    //create the legend
    var legend_tag = "<div class='legend'></div>";
    var legend_element = $(legend_tag)[0];
    chart_div.append(legend_element);

    var legend = d3.select(legend_element)
        .attr("style","display:block;width:"
            + canvas_width + "px;text-align:center")

    legend.selectAll("span")
        .data(fields)
        .enter()
        .append("span")
        .html(function(d){
            return "<span style='color:" + d["Color"] +";'> &#11044;</span>" + "&nbsp;" +
            d["Label"].replace(" ", "&nbsp;")
        })
        .attr("style", "padding-left:10px;padding-right:10px;")

    // setup the d3 svg selection
    var svg = d3.select(svg_element)
    var width = +svg.attr("width")
    var height = +svg.attr("height")
    var maxRadius = Math.min(width, height) / 2
    var g = svg.append("g").attr("transform",
    "translate(" + width / 2 + "," + height / 2 + ")");

    // Create the base chart and helper methods
    var color = d3.scaleOrdinal(fields.map(field => field["Color"]));
    var pie = d3.pie()
        .sort(null)
        .value(function(d) { return d; });
    var path = d3.arc()
        .outerRadius(maxRadius)
        .innerRadius(0);
    var arc = g.selectAll(".arc")
        .data(pie(fields.map(field => 0)))//Initialize the pie chart with dummy data
        .enter().append("g")
        .attr("class", "arc")

    arc.append("path")
        .attr("d", path)
        .style("fill", function(d, i) { return color(i); })
        .append("title")
            .text(function(d){return d.value})

    this.render = function(data) {
        //Update the pie chart each time new data comes in
        arc.data(pie(data))
            .select("path")
            .attr("d", path)
            .select("title")
            .text(function(d){
                return d.value + " : "
                + (((d.endAngle - d.startAngle)*100.0)
                / (Math.PI * 2)).toFixed(2)
                + "%"
            })
    }

    this.reset = function() {
        //Reset the chart by setting each field to 0
        arc.data(pie(fields.map(field => 0)))
            .enter().select("g")

        arc.select("path")
            .attr("d", path)
    }

}
