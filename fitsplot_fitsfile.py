from astropy.io import fits
from astropy.io.fits.hdu import(PrimaryHDU, ImageHDU)
import traitlets as tr

from fitsplot import FitsPlotter

class FitsPlotterFitsFile(FitsPlotter):

    fitsfile = tr.Unicode(allow_none=True)

    def __init__(self, fitsfile=None, hdu=0, figure=None, ax=None, interval=None, intervalkwargs=None, stretch=None,
                 stretchkwargs=None, cmap=None):
        super().__init__(figure, ax, interval, intervalkwargs, stretch, stretchkwargs, cmap=cmap)
        self.fitsfile = fitsfile
        self.hdu = hdu
        self._huds = None


    @property
    def data(self):
        self.open()
        if self._huds is not None and \
                (isinstance(self._huds[self.hdu], PrimaryHDU) or isinstance(self._huds[self.hdu], ImageHDU)):
            return self._huds[self.hdu].data
        else:
            return None

    def open(self):
        if self._huds is None and self.fitsfile:
            self._huds = fits.open(self.fitsfile, lazy_load_hdus=False)
            self._huds.info()

    def set_file(self, filename):
        self._huds = None
        self.fitsfile = filename

    @data.setter
    def data(self, d):
        raise TypeError('Can not set data directly in FitsPlotterFitsFile. Set fits file instead')

    @property
    def header(self):
        self.open()
        try:
            return self._huds[self.hdu].header
        except (TypeError, LookupError):
            return None

    def set_wcs(self, wcs):
        self.wcs = wcs
        try:
            self.ax.reset_wcs(wcs)
        except AttributeError: # ax is None or not WCSAxies
            pass


