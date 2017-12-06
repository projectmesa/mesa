var NetworkModule = function(canvas_width, canvas_height) {

    var div_tag = "<div id='graph-container' style='width: " +
        canvas_width + "px; height: " + canvas_height + "px;'></div>";

    // Append it to #elements:
    var div = $(div_tag)[0];
    $("#elements").append(div);

    var s = {
        container: 'graph-container',
        settings: {
            defaultNodeColor: 'black',
            minEdgeSize: 1,
            maxEdgeSize: 5
        }
    };

    this.render = function(data) {
        var graph = JSON.parse(JSON.stringify(data));

        // Update the instance's graph:
        if (s instanceof sigma) {
            s.graph.clear();
            s.graph.read(graph);
        }
        // ...or instantiate sigma if needed:
        else if (typeof s === 'object') {
            s.graph = graph;
            s = new sigma(s);
        }

        //Initialize nodes as a circle
        s.graph.nodes().forEach(function(node, i, a) {
            node.x = Math.cos(Math.PI * 2 * i / a.length);
            node.y = Math.sin(Math.PI * 2 * i / a.length);
        });

        //Call refresh to render the new graph
        s.refresh();
    };

    this.reset = function() {
        if (s instanceof sigma) {
            s.graph.clear();
            s.refresh();
        }
    };

};