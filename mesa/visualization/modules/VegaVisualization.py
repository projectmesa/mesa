import altair as alt
from mesa.visualization.ModularVisualization import VisualizationElement


class VegaVisualization(VisualizationElement):

    package_includes = ["VegaModule.js"]

    def __init__(self, specs):
        if not isinstance(specs, MesaSpec):
            raise NotImplementedError

        new_element = "new VegaModule({})".format(specs.spec.to_json())
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        model.datacollector.collect(model)
        df = model.datacollector.get_agent_vars_dataframe()
        latest = df.loc[model.schedule.steps]
        print(latest)
        return latest.to_json(orient='records')


class MesaSpec:
    pass


class GridSpec(MesaSpec):
    def __init__(self, model=None, size=None, x="x", y="y"):
        if not model and not size:
            raise RuntimeError("Please provide either model or size")
        if model:
            size = (model.grid.width, model.grid.height)

        self.spec = (
            alt.Chart(data=alt.NamedData("agents"))
            .mark_circle()
            .encode(
                alt.X(x, type="ordinal", scale=alt.Scale(domain=list(range(size[0])))),
                alt.Y(y, type="ordinal", scale=alt.Scale(domain=list(range(size[1])))),
                color="atype:N"
            )
        )

    @property
    def json(self):
        return self.spec.to_json()
