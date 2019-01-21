import altair as alt
import json
from mesa.visualization.ModularVisualization import VisualizationElement


class VegaVisualization(VisualizationElement):
    """Visualize a mesa model with a Vega(-Lite) specification

    Args:
        mesa_specs: Sequence of mesa specs
        vega_spec: A valid vega(-lite) specification
        filename: A valid vega(-lite) JSON file.

    Notes:
        If you provide a vega(-lite) specification, make sure you include both a
        `model` and an `agents` named data table.
        Specifications are not yet checked to be valid.
    """

    package_includes = ["VegaModule.js"]

    def __init__(self, mesa_specs=None, vega_spec=None, filename=None):
        if mesa_specs:
            try:
                spec = alt.vconcat(*[s.spec for s in mesa_specs]).to_json()
            except TypeError:
                spec = mesa_specs.spec.to_json()
        elif vega_spec:
            spec = vega_spec
            # TODO: Check if spec is valid, incl. NamedData sources "agents" and "model"
        elif filename:
            with open(filename) as f:
                spec = f.readlines()

        new_element = "new VegaModule({})".format(spec)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        data = self._get_data(model)
        return json.dumps(data)

    @staticmethod
    def _get_data(model):
        """Get agents and model data from the models datacollector."""
        dc = model.datacollector

        # Record and store agent data in dict
        agent_records = dc._record_agents(model)
        names = ["Step", "unique_id"] + list(dc.agent_reporters.keys())
        agent_data = [
            {key: value for (key, value) in zip(names, agent)}
            for agent in agent_records
        ]
        for agent in agent_data:
            agent["unique_id"] = str(agent["unique_id"])

        # Call model reporters and store model data in a dict
        if dc.model_reporters:
            for var, reporter in dc.model_reporters.items():
                dc.model_vars[var].append(reporter(model))

        model_data = {"Step": model.schedule.steps}
        for reporter in dc.model_reporters.keys():
            model_data[reporter] = dc.model_vars[reporter][-1]

        return {"model": model_data, "agents": agent_data}


class _MesaSpec:
    """Parent class for MesaSpecifications.

    Args:
        data: Either of {'model', 'agents'}
    """

    def __init__(self, data):
        self.spec = alt.Chart(data=alt.NamedData(data))

        self.slider = alt.binding_range(min=0, max=0, step=1)
        self.select_step = alt.selection_single(
            name="stp", fields=["Step"], bind=self.slider
        )

        self.agent_selector = alt.selection_single(name="agent_select", fields=["unique_id"], on="mouseover")

    @property
    def json(self):
        """Return specification in JSON format."""

        return self.spec.to_json()


class GridSpec(_MesaSpec):
    """Create a two-dimensional Grid spec.

    Args:
        width, height: integer of grid width and height
        x, y: names of x, y coordinates (default: "x", "y")
        color: Variable by which to color agents
    """

    def __init__(self, width, height, x="x", y="y", color=None):
        super().__init__("agents")

        if not color:
            color = alt.value("darkblue")
        else:
            color = color + ":N"

        self.spec = (
            self.spec.mark_point(size=120, filled=True)
            .encode(
                alt.X(x, type="ordinal", scale=alt.Scale(domain=list(range(width)))),
                alt.Y(y, type="ordinal", scale=alt.Scale(domain=list(range(height-1, -1, -1)))),
                color=alt.condition(self.agent_selector, color, alt.value("lightgray")),
                tooltip=[{"field": "unique_id", "type": "nominal"}],
            )
            .add_selection(self.select_step)
            .transform_filter(self.select_step)
            .add_selection(self.agent_selector)
        )


class ModelChartSpec(_MesaSpec):
    """Create a Chart spec from one or more model variables.

    Args:
        variables: variable name or list of variable names
    """

    def __init__(self, variables):
        super().__init__("model")

        if isinstance(variables, str):
            variables = [variables]
            specs = [self._create_single_spec(variable) for variable in variables]

        variables = [v + ":N" for v in variables]
        rule = (
            self.spec.mark_rule(color="gray")
            .encode(x="Step:Q", tooltip=variables)
            .add_selection(self.select_step)
            .transform_filter(self.select_step)
        )

        self.spec = alt.layer(*specs, rule)

    def _create_single_spec(self, variable):
        """Create chart spec from a single variable."""
        spec = self.spec.mark_line().encode(
            alt.X("Step", type="quantitative"), alt.Y(variable, type="quantitative")
        )
        return spec


class AgentChartSpec(_MesaSpec):
    """Create a chart spec for the mean of a single agent variable.

    Args:
        variable: agent variable name
    """

    def __init__(self, variable):
        super().__init__("agents")

        spec = (
            self.spec.mark_line()
            .encode(
                x=alt.X("Step", type="quantitative"),
                y=alt.Y("neighbors", type="quantitative", aggregate="mean")
            )
            .add_selection(self.agent_selector)
            .transform_filter(self.agent_selector)
        )

        rule = (
            self.spec.mark_rule(color="gray")
            .encode(x="Step:Q", tooltip=variable + ":N")
            .add_selection(self.select_step)
            .transform_filter(self.select_step)
        )

        self.spec = alt.layer(spec, rule)
