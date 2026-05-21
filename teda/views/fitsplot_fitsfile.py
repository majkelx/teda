import logging
from astropy.io import fits
from astropy.io.fits.hdu import(PrimaryHDU, ImageHDU, CompImageHDU)
import traitlets as tr

from .fitsplotcontrolled import FitsPlotterControlled

logger = logging.getLogger(__name__.rsplit('.')[-1])

_IMAGE_HDU_TYPES = (PrimaryHDU, ImageHDU, CompImageHDU)


def _is_image_hdu(hdu):
    """Return True if the HDU can hold a 2D+ image (incl. tile-compressed)."""
    return isinstance(hdu, _IMAGE_HDU_TYPES)


def _first_image_hdu_index(hduls):
    """Index of the first HDU that actually carries image data, or 0 as fallback.

    A PRIMARY HDU without NAXIS (common in tile-compressed files) is skipped in
    favor of the COMPRESSED_IMAGE extension that follows it.
    """
    for i, hdu in enumerate(hduls):
        if not _is_image_hdu(hdu):
            continue
        if isinstance(hdu, CompImageHDU):
            return i
        if getattr(hdu, 'shape', None):
            return i
    return 0


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
        if self._huds is not None and _is_image_hdu(self._huds[self.hdu]):
            try:
                return self._huds[self.hdu].data
            except ValueError as e:
                # Handle memmap incompatibility detected during lazy data access
                logger.warning(f'Error accessing data: {e}. Attempting to reload without memmap')
                # Close current file and reload without memmap
                self._huds.close()
                try:
                    self._huds = fits.open(self.fitsfile, lazy_load_hdus=True, memmap=False)
                    return self._huds[self.hdu].data
                except Exception as e2:
                    logger.error(f'Failed to reload file: {e2}')
                    return None
        else:
            return None

    def open(self):
        if self._huds is None and self.fitsfile:
            try:
                self._huds = fits.open(self.fitsfile, lazy_load_hdus=True, memmap=True)
            except (OSError, ValueError) as e:
                # ValueError: memmap incompatible with BZERO/BSCALE scaling
                # Fallback to memmap=False
                logger.warning(f'Cannot use memmap for {self.fitsfile}: {e}. Falling back to memmap=False')
                self._huds = fits.open(self.fitsfile, lazy_load_hdus=True, memmap=False)
            self._huds.info()
            self.hdu = _first_image_hdu_index(self._huds)

    def set_file(self, filename):
        if filename is not None:
            try:
                self._huds = fits.open(filename, lazy_load_hdus=True, memmap=True)
                self._huds.info()
            except ValueError as e:
                # memmap incompatible with BZERO/BSCALE scaling - retry without memmap
                logger.warning(f'Cannot use memmap for {filename}: {e}. Falling back to memmap=False')
                try:
                    self._huds = fits.open(filename, lazy_load_hdus=True, memmap=False)
                    self._huds.info()
                except (FileNotFoundError, OSError) as e2:
                    logger.error(f'Cannot open file {filename}: {e2}')
                    self._huds = None
            except (FileNotFoundError, OSError) as e:
                logger.error(f'Cannot open file {filename}: {e}')
                self._huds = None
        else:
            self._huds = None
        if self._huds is not None:
            self.hdu = _first_image_hdu_index(self._huds)
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



