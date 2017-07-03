/**
 * JSONloader reads JSON files and returns them as an Object.
 * @param input The <input> tag used for file input
 * @param callback The callback to call on success.
 * @constructor Default constructor
 */

function JSONloader(input, callback) {
    document.getElementById(input)
        .addEventListener('change', function (e) {
            var el = e.target;
            if (el.files && el.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    var data = window.atob(e.target.result.replace('data:;base64,', ''));
                    callback(JSON.parse(data));
                };
                reader.readAsDataURL(el.files[0]);
            }
        }
    );
}
