var res;

var vegaGrid = function () {
    // Create and append the element:
    const vega_element = document.createElement("div");
    vega_element.setAttribute("id", "vega");
    document.getElementById("elements").appendChild(vega_element);

    const spec = 'local/conways_game_of_life/gridSpec.json'

    // Use vegaEmbed to visualize the specification
    const resurrectCells = function (name, value) {
        send({ "type": "call_method", "method_name": "resurrect", "arguments": value })
    };

    const create_chart = async function () {
        let grid = await vegaEmbed("#vega", spec, {
            "patch": {
                "signals": [
                    { "name": "position", "on": [{ "events": "click, mousemove[event.buttons]", "update": "[invert('x', x()), invert('y', y())]" }] }
                ]
            }
        })
        res = grid
        grid.view.addSignalListener("position", resurrectCells)
        return grid
    };

    this.render = async function (data) {
        data = JSON.parse(data)
        if (typeof (this.grid) === 'undefined') {
            this.grid = await create_chart()
        }
        let agents_changeset = vega.changeset()
            .insert(data)
            .remove(vega.truthy)
        this.grid.view.change('cells', agents_changeset).run()
    };

    this.reset = async function () {
        this.grid = await create_chart()
    };
};