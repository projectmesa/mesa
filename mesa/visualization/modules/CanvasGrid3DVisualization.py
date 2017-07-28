from mesa.visualization.modules import CanvasGrid


class CanvasGrid3D(CanvasGrid):
    """ A subclass of CanvasGrid that displays in 3D """

    package_includes = ["three.min.js", "OrbitControls.js", "Canvas3DModule.js"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the initialization of js_code
        self.js_code = (
            "elements.push ({});".format(
                "new Canvas3DModule({}, {}, {}, {})".format(
                    self.canvas_width, self.canvas_height, self.grid_width, self.grid_height)
            )
        )
