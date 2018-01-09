/**
 * JSONLoader reads JSON files and returns them as an Object.
 * Data and <input> file tag are available as member variables.
 * @param input The <input> tag used for file input.
 * @param callback The success callback to call when data is loaded in the browser. Callback has one argument, 'data',
 * which is an Object with the same structure as that provided from the result of pinging the server via `send({'type': 'get_params'})`.
 * An example callback would look something like this:
 * ```
 * function successCallback(data) {
 *     console.log(data);  // Print the loaded JSON object
 * }
 * ```
 */

function JSONLoader(input, callback) {

    this.input = input;
    this.data = {};
    var self = this;

    document.getElementById(input)
        .addEventListener('change', function (e) {
            var el = e.target;
            if (el.files && el.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    var data = JSON.parse(window.atob(e.target.result.replace('data:application/json;base64,', '')));
                    callback(data);
                    self.data = data;
                };
                reader.readAsDataURL(el.files[0]);
            }
        }
    );
}
