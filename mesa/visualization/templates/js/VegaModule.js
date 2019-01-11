var res;

var VegaModule = function (spec) {
	// Create the element
	// ------------------

	// Create the tag:
	var vega_tag = "<div id='vega'></div>"
	// Append it to body:
	var vega_element = $(vega_tag)[0];
	$("#elements").append(vega_element);

	// Create the context and the drawing controller:
	console.log(spec)
	vegaEmbed('#vega', spec).then(function (result) {
		// Access the Vega view instance (https://vega.github.io/vega/docs/api/view/) as result.view
		res = result
	}).catch(console.error);

	this.render = function (data) {
		data = JSON.parse(data)
		stp_element = document.getElementsByName("stp_Step")[0]
		stp_element["max"] = data["model"]["Step"]

		res.view.signal("stp_Step", data["model"]["Step"])

		var agents_changeset = vega.changeset()
			.insert(data["agents"])
			.remove(vega.truthy)
		// res.view.change('agents', agents_changeset)
		res.view.insert("agents", data["agents"])
		res.view.insert('model', data['model']).run()


	};

	this.reset = function () {
		res.view.remove("agents", vega.truthy)
		res.view.remove("model", vega.truthy).run()
	};

};
