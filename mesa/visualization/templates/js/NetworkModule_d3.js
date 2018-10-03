var NetworkModule = function(svg_width, svg_height) {

    // Create the svg tag:
    var svg_tag = "<svg width='" + svg_width + "' height='" + svg_height + "' " +
        "style='border:1px dotted'></svg>";

    // Append svg to #elements:
    $("#elements")
        .append($(svg_tag)[0]);

    var svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height"),
        g = svg.append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    svg.call(d3.zoom()
        .on("zoom", function() {
            g.attr("transform", d3.event.transform);
        }));

    this.render = function(data) {
        var graph = JSON.parse(JSON.stringify(data));

        var simulation = d3.forceSimulation(graph.nodes)
            .force("charge", d3.forceManyBody()
                .strength(-80)
                .distanceMin(6))
            .force("link", d3.forceLink(graph.edges))
            .force("center", d3.forceCenter())
            .stop();

        var loading = svg.append("text")
            .attr("dy", "0.35em")
            .attr("text-anchor", "middle")
            .attr("font-family", "sans-serif")
            .attr("font-size", 10)
            .text("Simulating. One moment please…");

        // Use a timeout to allow the rest of the page to load first.
        d3.timeout(function() {
            loading.remove();

            for (var i = 0, n = Math.ceil(Math.log(simulation.alphaMin()) / Math.log(1 - simulation.alphaDecay())); i < n; ++i) {
                simulation.tick();
            }

            var links = g.append("g")
                .selectAll("line")
                .data(graph.edges);
            links.enter()
                .append("line")
                .attr("x1", function(d) { return d.source.x; })
                .attr("y1", function(d) { return d.source.y; })
                .attr("x2", function(d) { return d.target.x; })
                .attr("y2", function(d) { return d.target.y; })
                .attr("stroke-width", function(d) { return d.width; })
                .attr("stroke", function(d) { return d.color; });

            links.exit()
                .remove();

            var nodes = g.append("g")
                .selectAll("circle")
                .data(graph.nodes);
            nodes.enter()
                .append("circle")
                .attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; })
                .attr("r", function(d) { return d.size; })
                .attr("fill", function(d) { return d.color; })
                .on("mouseover", function(d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(d.tooltip)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY) + "px");
                })
                .on("mouseout", function() {
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                });

            nodes.exit()
                .remove();
        });
    };

    this.reset = function() {
        reset();
    };

    function reset() {
        svg.selectAll("g")
            .remove();
        g = svg.append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

        svg.call(d3.zoom()
            .on("zoom", function() {
                g.attr("transform", d3.event.transform);
            }));
    }
};