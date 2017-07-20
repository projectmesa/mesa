var NetworkModule = function(svg_width, svg_height) {

    // Create the svg tag:
    var svg_tag = "<svg width='" + svg_width + "' height='" + svg_height + "' " +
        "style='border:1px dotted'></svg>";

    //Create the style:
    var style_tag = "<style>" +
        ".links line {" +
        "  stroke-opacity: 0.6;" +
        "}" +
        ".nodes circle {" +
        "  stroke: #fff;" +
        "  stroke-width: 1.5px;" +
        "}" +
        "</style>"

    // Append style to body:
    $("body").append($(style_tag)[0]);

    // Append svg to #elements:
    $("#elements").append($(svg_tag)[0]);

    var svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    var simulation = d3.forceSimulation()
        .force("link", d3.forceLink().id(function(d) {
            return d.id;
        }))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    var g_links = svg.append("g").attr("class", "links");
    var g_nodes = svg.append("g").attr("class", "nodes");

    this.render = function(data) {
        var graph = JSON.parse(JSON.stringify(data));

        simulation.alphaTarget(0.3).restart();

        var link = g_links.selectAll("line").data(graph.links);
        link.attr("stroke-width", function(d) {
                return d.width;
            })
            .attr("stroke", function(d) {
                return d.color;
            });
        link.exit().remove();
        link.enter().append("line");


        var node = g_nodes.selectAll("circle").data(graph.nodes);
        node.attr("fill", function(d) {
                return d.color;
            })
            .attr("r", 6)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .append("title")
            .text(function(d) {
                return d.id;
            });
        node.exit().remove();
        node.enter().append("circle");

        simulation
            .nodes(graph.nodes)
            .on("tick", ticked);

        simulation
            .force("link")
            .links(graph.links);

        function ticked() {
            link
                .attr("x1", function(d) {
                    return d.source.x;
                })
                .attr("y1", function(d) {
                    return d.source.y;
                })
                .attr("x2", function(d) {
                    return d.target.x;
                })
                .attr("y2", function(d) {
                    return d.target.y;
                });

            node
                .attr("cx", function(d) {
                    return d.x;
                })
                .attr("cy", function(d) {
                    return d.y;
                });
        }
    };

    this.reset = function() {
        d3.select("svg").selectAll("g").remove();
        g_links = d3.select("svg").append("g").attr("class", "links");
        g_nodes = d3.select("svg").append("g").attr("class", "nodes");
    };

    function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
};