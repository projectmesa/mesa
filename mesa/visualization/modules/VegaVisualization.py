import json
from typing import List

from mesa.visualization.ModularVisualization import VisualizationElement
from mesa.model import Model


class VegaModule(VisualizationElement):
    package_includes = [
        "vega-lite.min.js",
        "vega.min.js",
        "vegaEmbed.min.js",
        "vegaModule.js",
    ]

    def __init__(
        self,
        spec: str,
        agent_attributes: List[str] = None,
        model_attributes: List[str] = None,
    ) -> None:
        """Create a Vega Visualization Element.

        Args:
            spec: Vega or Vega-lite specification as a JSON string. See notes
            model_attributes: List of model attributes to include in data
            agent_attributes: List of agent attributes to include in data

        Notes:
            The specification should have its data specified as follows:
            "data": {"name": "model"}
            If neither model nor agent attributes are provided,
            all model and agent attributes will be included.
        """
        self.agent_attributes = agent_attributes
        self.model_attributes = model_attributes
        self.js_code = "elements.push(new vegaModule({}));".format(spec)

    def render(self, model: Model) -> None:
        """Create a JSON data table from a model."""
        if self.model_attributes is None and self.agent_attributes is None:
            try:
                return model.as_json()
            except AttributeError:
                print("Please provide either model or agent attributes")
        model_state = {}
        agent_states = []
        if self.model_attributes:
            model_state = {
                attribute: getattr(model, attribute, None)
                for attribute in self.model_attributes
            }
        if self.agent_attributes:
            for agent in model.schedule.agents:
                agent_states.append(
                    {
                        attribute: getattr(agent, attribute, None)
                        for attribute in self.agent_attributes
                    }
                )
        state = model_state["agents"] = agent_states

        return json.dumps(state)
