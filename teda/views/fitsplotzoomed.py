from matplotlib import patches
from .fitsplotcontrolled import FitsPlotterControlled


class FitsPlotterZoomed(FitsPlotterControlled):

    def __init__(self, figure=None, ax=None, interval=None, intervalkwargs=None, stretch=None, stretchkwargs=None,
                 cmap_model=None, scale_model=None):
        self.mouse_box = None
        super().__init__(figure, ax, interval, intervalkwargs, stretch, stretchkwargs,
                         cmap_model=cmap_model, scale_model=scale_model)

    def plot_fits_data(self, data, ax, alpha, norm, cmap):

        super().plot_fits_data(data, ax, alpha=alpha, norm=norm, cmap=cmap)
        if self.mouse_box is None:
            self.mouse_box = patches.Rectangle(
                (data.shape[0]/2 + 0.5, data.shape[0]/2 + 0.5), 1.0, 1.0,
                linewidth=1, edgecolor='r', fill=False,
            )
            ax.add_patch(self.mouse_box)

    def moveToXYcordsWithZoom(self, x, y, zoom, fits, idle=True):
        self.mouse_box.set_xy([x-0.5, y-0.5])
        super().moveToXYcordsWithZoom(x, y, zoom, fits, idle)

    # def moveToXYcordsWithZoom(self, x, y, zoom, fits, idle=True):
