var res = undefined;

var VegaModule = function(spec) {
	// Create the element
	// ------------------

    // Create the tag:
    var vega_tag = "<div id='vega'></div>"
	// Append it to body:
	var vega_element = $(vega_tag)[0];
	$("#elements").append(vega_element);

	// Create the context and the drawing controller:
    var spec = spec;
    vegaEmbed('#vega', spec).then(function(result) {
	  // Access the Vega view instance (https://vega.github.io/vega/docs/api/view/) as result.view
	  res = result
    }).catch(console.error);

	this.render = function(data) {
		data = JSON.parse(data)
		var changeset = vega.changeset()
            .insert(data)
            .remove(vega.truthy)
		res.view.change('agents', changeset).run()
	};

	this.reset = function() {
	};

};
