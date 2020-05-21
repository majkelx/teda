from astropy.wcs import WCS, InvalidTransformError
from traitlets import HasTraits, Int, Float
from random import random


class CoordinatesModel(HasTraits):
    img_x = Float(allow_none=True)
    img_y = Float(allow_none=True)
    img_versionno = Int()  # observe this for single signal on (img_x, img_y) change
    img_col = Int(allow_none=True)
    img_row = Int(allow_none=True)
    wcs_x_deg = Float(allow_none=True)
    wcs_y_deg = Float(allow_none=True)
    wcs_deg_versionno = Int()   # observe this for single signal on (wcs_x_deg,wcs_y_deg) change

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wcs = None
        self.observe(lambda change: self.on_img_coords_change(change), ['img_x', 'img_y'])

    def on_img_coords_change(self, change):
        pass

    def set_wcs_from_fits(self, fits_header):
        try:
            try:
                wcs = WCS(fits_header, translate_units='sdh')
            except InvalidTransformError:  # Remove scamp distortion
                h = fits_header.header.copy()
                for i in range(11):
                    for pv in ['PV1_{:d}', 'PV2_{:d}']:
                        h.remove(pv.format(i), ignore_missing=True, remove_all=True)
                wcs = WCS(h, translate_units='sdh')
        except Exception:
            wcs = None
        self.set_wcs(wcs)

    def set_wcs(self, wcs: WCS):
        self.wcs = wcs
        self.calc_wcs()

    def calc_wcs(self):
        change = False
        if self.wcs is None or self.img_x is None or self.img_y is None:
            if self.wcs_x_deg is not None:
                self.wcs_x_deg = None
                change = True
            if self.wcs_y_deg is not None:
                self.wcs_y_deg = None
                change = True
        else:
            world = self.wcs.pixel_to_world_values(self.img_x, self.img_y)
            wx, wy = float(world[0]), float(world[1])
            if self.wcs_x_deg != wx:
                self.wcs_x_deg = wx
                change = True
            if self.wcs_y_deg != wy:
                self.wcs_y_deg = wy
                change = True
        if change:
            self.wcs_deg_versionno += 1


    def set_img_xy(self, x, y):
        self.img_x = x
        self.img_y = y
        self.calc_wcs()
        self.img_versionno += 1

    def set_img_x(self, x):
        self.img_x = x
        self.calc_wcs()
        self.img_versionno += 1

    def set_img_y(self, y):
        self.img_y = y
        self.calc_wcs()
        self.img_versionno += 1



