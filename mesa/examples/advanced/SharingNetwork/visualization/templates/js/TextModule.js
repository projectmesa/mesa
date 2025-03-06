var TextModule = function() {
	var tag = "<p class='lead'></p>";
	var text = $(tag)[0];

	// Append text tag to #elements:
    $("#elements").append(text);

	this.render = function(data) {
		$(text).html(data);
	};

	this.reset = function() {
		$(text).html("");
	};
};