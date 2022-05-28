const TextModule = function () {
  const text = document.createElement("p");
  text.className = "lead";

  // Append text tag to #elements:
  document.getElementById("elements").appendChild(text);

  this.render = function (data) {
    text.innerHTML = data;
  };

  this.reset = function () {
    text.innerHTML = "";
  };
};
