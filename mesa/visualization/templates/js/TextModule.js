var TextModule = function() {
	var tag = "<p></p>";
	var text = $(tag)[0];
	$("body").append(text);

	this.render = function(data) {
		$(text).html(data);
	};

	this.reset = function() {
		$(text).html("");
	};
};