from astropy.wcs import WCS, InvalidTransformError
from astropy.coordinates import SkyCoord
from traitlets import HasTraits, Int, Float, Bool, Unicode


class CoordinatesModel(HasTraits):
    img_x = Float(allow_none=True)
    img_y = Float(allow_none=True)
    img_versionno = Int()  # observe this for single signal on (img_x, img_y) change
    img_col = Int(allow_none=True)
    img_row = Int(allow_none=True)
    wcs_deg_versionno = Int()   # observe this for single signal on (wcs_x_deg,wcs_y_deg) change

    wcs_sexagesimal = Bool(False)
    wcs_formatted = Unicode('no WCS')
    wcs_framename = Unicode('WCS')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wcs = None
        self.observe(lambda change: self.on_img_coords_change(change), ['img_x', 'img_y'])
        self.observe(lambda change: self.format_wcs(), ['wcs_sexagesimal'])
        self.wcs_coo = None

    def on_img_coords_change(self, change):
        pass

    def set_wcs_from_fits(self, fits_header):
        try:
            try:
                wcs = WCS(fits_header, translate_units='sdh')
            except InvalidTransformError:  # Remove scamp distortion
                h = fits_header.copy()
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
        try:
            if self.wcs is None or self.img_x is None or self.img_y is None:
                raise ValueError()
            world = SkyCoord.from_pixel(self.img_x, self.img_y, wcs=self.wcs)
            if self.wcs_coo is None or self.wcs_coo != world:
                self.wcs_coo = world
                change = True

        except ValueError:
            if self.wcs_coo is not None:
                self.wcs_coo = None
                change = True

        if change:
            self.wcs_deg_versionno += 1
            self.format_wcs()

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

    def format_wcs(self):
        if self.wcs_coo is not None:
            if self.wcs_sexagesimal:
                self.wcs_formatted = self.wcs_coo.to_string('hmsdms', sep=':', precision=3)
            else:
                self.wcs_formatted = self.wcs_coo.to_string('decimal', precision=3)
            self.wcs_framename = self.wcs_coo.name
        else:
            self.wcs_formatted = ''
            self.wcs_framename = 'WCS'
