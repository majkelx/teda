import logging
from astropy.io import fits
from astropy.io.fits.hdu import(PrimaryHDU, ImageHDU)
import traitlets as tr

from .fitsplotcontrolled import FitsPlotterControlled

logger = logging.getLogger(__name__.rsplit('.')[-1])


class FitsPlotterFitsFile(FitsPlotterControlled):

    fitsfile = tr.Unicode(allow_none=True)

    def __init__(self, fitsfile=None, hdu=0, figure=None, ax=None, interval=None, intervalkwargs=None, stretch=None,
                 stretchkwargs=None, cmap_model=None, scale_model=None):
        self.fitsfile = fitsfile
        self.hdu = hdu
        self._huds = None
        super().__init__(figure, ax, interval, intervalkwargs, stretch, stretchkwargs,
                         cmap_model=cmap_model, scale_model=scale_model)


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
            self._huds = fits.open(self.fitsfile, lazy_load_hdus=True, memmap=True)
            self._huds.info()

    def set_file(self, filename):
        if filename is not None:
            try:
                self._huds = fits.open(filename, lazy_load_hdus=True, memmap=True)
                self._huds.info()
            except (FileNotFoundError, OSError) as e:
                logger.error(f'Can not open file {filename}: {e}')
        else:
            self._huds = None
        self.fitsfile = filename

    @data.setter
    def data(self, d):
        raise TypeError('Can not set data directly in FitsPlotterFitsFile. Set fits file instead')

    def changeHDU(self, relative, val):
        if relative:
            self.hdu = self.hdu + val
        else:
            self.hdu = val
        if self.hdu < 0:
            self.hdu = 0
        elif self.hdu > len(self._huds) - 1:
            self.hdu = len(self._huds) - 1

        self.reset_ax()
        self.plot()

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

    def isFitsFile(self,filename,showinfo = True):
        try:
            fits.open(filename)
            return True
        except FileNotFoundError as e:
            if showinfo:
                logger.error(f'Can not find file {filename}: {e}')
            return False
        except OSError as e:
            if showinfo:
                logger.error(f'Can not open file {filename}: {e}')
            return False



