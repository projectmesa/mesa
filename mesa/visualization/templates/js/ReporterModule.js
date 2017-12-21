var ReporterModule = function() {
	var dropdown_button = '<button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select Reporter</button>'
  var dropdown_menu = '<div class="dropdown-menu" aria-labelledby="dropdownMenuButton"></div>'
	var item = '<a class="dropdown-item" href="#"></a>'
  var item_input = $(item)[0]

	// Append text tag to #elements:
    $("#elements").append(dropdown_button)
    $("#dropdownMenuButton").append(dropdown_menu);

	this.render = function(data) {
		$(".dropdown-menu").append(item);
    $(".dropdown-item").html(data)
	};

	this.reset = function() {
		$(item).html("");
	};
};
