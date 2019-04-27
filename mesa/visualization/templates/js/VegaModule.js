const vegaModule = function (spec) {
    // Create and append the element:
    const vega_element = document.createElement("div");
    vega_element.setAttribute("id", "vega");
    document.getElementById("elements").appendChild(vega_element);

    const create_chart = async function () {
        const result = await vegaEmbed("#vega", spec)
        return result.view
    };

    this.view = create_chart()

    this.render = async function (data) {
        data = JSON.parse(data)
        let changeset = vega.changeset()
            .insert(data)
            .remove(vega.truthy)
        this.view.change('model', changeset).run()
    };

    this.reset = async function () {
        this.view = await create_chart()
        console.log(this.view)
    };
};
