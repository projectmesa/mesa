from collections import defaultdict

from mesa.visualization.modules import CanvasGrid


class CanvasGrid3D(CanvasGrid):
    """ A subclass of CanvasGrid that displays in 3D """

    package_includes = ["three.min.js", "OrbitControls.js", "Canvas3DModule.js"]

    def __init__(self, *args, **kwargs):
        self.flip_y = kwargs.pop('flip_y', False)
        super().__init__(*args, **kwargs)

        # Override the initialization of js_code
        self.js_code = (
            "elements.push ({});".format(
                "new Canvas3DModule({}, {}, {}, {}, {})".format(
                    self.canvas_width, self.canvas_height, self.grid_width, self.grid_height,
                    'true' if self.flip_y else 'false'
                )
            )
        )

    def render(self, model):
        if not hasattr(model, 'grid'):
            if hasattr(model, 'space'):
                grid_state = defaultdict(list)
                for obj in model.schedule.agents:
                    portrayal = self.portrayal_method(obj)
                    x, y = obj.pos
                    x = ((x - model.space.x_min) /
                         (model.space.x_max - model.space.x_min))
                    y = ((y - model.space.y_min) /
                         (model.space.y_max - model.space.y_min))
                    portrayal["x"] = x * model.space.width
                    portrayal["y"] = y * model.space.height
                    grid_state[0].append(portrayal)
                return grid_state
            else:
                return None
        else:
            return super().render(model)
