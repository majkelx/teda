from matplotlib import patches
from fitsplot import FitsPlotter

class FitsPlotterControlled(FitsPlotter):
    """Extend FitsPlotter for MVC Controller functionality to connect to the model"""

    def __init__(self, figure=None, ax=None, interval=None, intervalkwargs=None, stretch=None, stretchkwargs=None,
                 cmap=None, scale_model=None):
        self.mouse_box = None
        self.scale_model = None
        super().__init__(figure, ax, interval, intervalkwargs, stretch, stretchkwargs, cmap=cmap)
        self.set_scale_model(scale_model)
        self.scale_from_model()

    def scale_from_model(self):
        if self.scale_model is None:
            return
        stretch  = self.scale_model.selected_stretch
        interval = self.scale_model.selected_interval

        self.set_normalization(stretch=stretch,
                               interval=interval,
                               stretchkwargs=self.scale_model.dictionary[stretch],
                               intervalkwargs=self.scale_model.dictionary[interval]
                               )
        self.invalidate()

    def set_scale_model(self, scale_model):
        self.scale_model = scale_model
        if scale_model is not None:
            scale_model.observe(lambda change: self.on_scale_model_change(change))
        self.scale_from_model()

    def on_scale_model_change(self, change):
        self.scale_from_model()

