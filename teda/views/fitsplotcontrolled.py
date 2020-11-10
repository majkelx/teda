from matplotlib import patches
from .fitsplot import FitsPlotter

class FitsPlotterControlled(FitsPlotter):
    """Extend FitsPlotter for MVC Controller functionality to connect to the model"""

    def __init__(self, figure=None, ax=None, interval=None, intervalkwargs=None, stretch=None, stretchkwargs=None,
                 cmap_model=None, scale_model=None):
        self.mouse_box = None
        self.scale_model = None
        self.cmap_model = None
        super().__init__(figure, ax, interval, intervalkwargs, stretch, stretchkwargs)
        self.set_scale_model(scale_model)
        self.set_cmap_model(cmap_model)
        self.scale_from_model()
        self.cmap_from_model()

    def scale_from_model(self):
        if self.scale_model is None:
            return

        selected_stretch = self.scale_model.selected_stretch
        selected_interval = self.scale_model.selected_interval

        if selected_stretch != 'linear':
            self.set_normalization(stretch=selected_stretch,
                                   interval=selected_interval,
                                   stretchkwargs=self.scale_model.dictionary[selected_stretch],
                                   intervalkwargs=self.scale_model.dictionary[selected_interval],
                                   perm_linear=self.scale_model.dictionary['linear'])
        else:
            self.set_normalization(stretch=selected_stretch,
                                   interval=selected_interval,
                                   stretchkwargs=self.scale_model.dictionary[selected_stretch],
                                   intervalkwargs=self.scale_model.dictionary[selected_interval])

        self.invalidate()

    def cmap_from_model(self):
        if self.cmap_model is None:
            return
        self.set_cmap(self.cmap_model.get_active_color_map())
        self.invalidate()

    def set_scale_model(self, scale_model):
        self.scale_model = scale_model
        if scale_model is not None:
            scale_model.observe(lambda change: self.on_scale_model_change(change))
        self.scale_from_model()

    def set_cmap_model(self, cmap_model):
        self.cmap_model = cmap_model
        if cmap_model is not None:
            cmap_model.observe(lambda change: self.on_cmap_model_change(change))
        self.cmap_from_model()

    def on_scale_model_change(self, change):
        self.scale_from_model()

    def on_cmap_model_change(self, change):
        self.cmap_from_model()
