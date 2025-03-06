'use strict';
// Note: This grouped bar chart is based off the example found here:
// https://bl.ocks.org/mbostock/3887051
var BarChartModule = function(fields, canvas_width, canvas_height, sorting, sortingKey) {
    // Create the overall chart div
    var chart_div_tag = "<div class='bar chart' width='" + canvas_width + "'></div>";
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
    var margin = {top: 20, right: 20, bottom: 30, left: 40}
    var width = +svg.attr("width") - margin.left - margin.right
    var height = +svg.attr("height") - margin.top - margin.bottom
    var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Setup the bar chart
    var x0 = d3.scaleBand()
        .rangeRound([0, width])
        .paddingInner(0.1);
    var x1 = d3.scaleBand()
        .padding(0.05);
    var y = d3.scaleLinear()
        .rangeRound([height, 0]);
    var colorScale = d3.scaleOrdinal(fields.map(field => field["Color"]));
    var keys = fields.map(f => f['Label'])
    var chart = g.append("g")
    var axisBottom = g.append("g")
    var axisLeft = g.append("g")

    axisBottom
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x0));

    axisLeft
        .attr("class", "axis")
        .call(d3.axisLeft(y).ticks(null, "s"))


    //Render step
    this.render = function(data){
        //Axes
        var minY = d3.min(data, function(d){
            return d3.min(keys, function(key){
                return d[key];
            })
        })
        if(minY > 0){
            minY = 0;
        }
        var maxY = d3.max(data, function(d){
            return d3.max(keys, function(key){
                return d[key];
            })
        })

        x0.domain(data.map(function(d, i) { return i }));
        x1.domain(keys).rangeRound([0, x0.bandwidth()]);
        y.domain([minY,maxY]).nice();

        if(data.length > 1){
            axisBottom
                .attr("transform", "translate(0," + y(0) + ")")
                .call(d3.axisBottom(x0))
        }

        axisLeft.call(d3.axisLeft(y).ticks(null, "s"))

        //Sorting
        if(sorting != "none"){
            if(sorting == "ascending"){
                data.sort((a, b) => b[sortingKey] - a[sortingKey]);
            } else if (sorting == "descending") {
                data.sort((a, b) => a[sortingKey] - b[sortingKey]);
            }
        }

        //Draw Chart
        var rects = chart
            .selectAll("g")
            .data(data)
            .enter().append("g")
                .attr("transform", function(d, i) { return "translate(" + x0(i) + ",0)"; })
            .selectAll("rect")

        rects
            .data(function(d) {
                return keys.map(function(key) {
                    return {key: key, value: d[key]};
                });
            })
            .enter()
                .append("rect")
                    .attr("x", function(d) { return x1(d.key); })
                    .attr("width", x1.bandwidth())
                    .attr("fill", function(d) { return colorScale(d.key); })
                    .attr("y", function(d) { return Math.min(y(d.value),y(0)); })
                    .attr("height", function(d) { return Math.abs(y(d.value) - y(0)); })
                .append("title")
                    .text(function (d) { return d.value; })

        //Update chart
        chart
            .selectAll("g")
            .data(data)
            .selectAll("rect")
            .data(function(d) {
                return keys.map(function(key) {
                    return {key: key, value: d[key]};
                });
            })
            .attr("y", function(d) { return Math.min(y(d.value),y(0)); })
            .attr("height", function(d) { return Math.abs(y(d.value) - y(0)); })
            .select("title")
                .text(function (d) { return d.value; })


    }

    this.reset = function(){
        chart.selectAll("g")
            .data([])
            .exit().remove();

    }

}
