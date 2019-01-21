var res;

var VegaModule = function(spec) {
  // Create and append the element:
  vega_element = document.createElement("div");
  vega_element.setAttribute("id", "vega");
  document.getElementById("elements").appendChild(vega_element);

  // Use vegaEmbed to visualize the specification
  console.log(spec);
  vegaEmbed("#vega", spec)
    .then(function(result) {
      // Access the Vega view instance (https://vega.github.io/vega/docs/api/view/) as result.view
      res = result;
    })
    .catch(console.error);

  this.render = function(data) {
    data = JSON.parse(data);
    // adjust length of stp_element
    stp_element = document.getElementsByName("stp_Step")[0];
    stp_element["max"] = data["model"]["Step"];

    res.view.signal("stp_Step", data["model"]["Step"]);
    res.view.insert("agents", data["agents"]);
    res.view.insert("model", data["model"]).run();

    /* instead of adding the agent data we could also exchange it
	  var agents_changeset = vega.changeset()
		.insert(data["agents"])
		.remove(vega.truthy)
	  res.view.change('agents', agents_changeset)
	  */
  };

  this.reset = function() {
    res.view.remove("agents", vega.truthy);
    res.view.remove("model", vega.truthy).run();
  };
};
