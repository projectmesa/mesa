const TextModule = function() {
	const tag = "<p class='lead'></p>";
	const text = $(tag)[0];

	// Append text tag to #elements:
    $("#elements").append(text);

	this.render = function(data) {
		$(text).html(data);
	};

	this.reset = function() {
		$(text).html("");
	};
};