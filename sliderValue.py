from traitlets import HasTraits, Int, Float


class SliderValue(HasTraits):
    stretch_asinh_a = Int(5)
    stretch_contrast_contrast = Int(20)
    stretch_contrast_bias = Int(10)
    stretch_linear_slope = Int(10)
    stretch_linear_intercept = Int()
    stretch_log_a = Int()
    stretch_powerdist_a = Int()
    stretch_power_a = Int()
    stretch_sinh_a = Int()

    interval_manual_vmin = Int()
    interval_manual_vmax = Int()
    interval_percentile_percentile = Int()
    interval_percentile_nsamples = Int()
    interval_asymetric_lpercentile = Int()
    interval_asymetric_upercentile = Int()
    interval_asymetric_nsamples = Int()
    interval_zscale_nsamples = Int()
    interval_zscale_contrast = Int()
    interval_zscale_maxreject = Int(5)
    interval_zscale_minpixels = Int(5)
    interval_zscale_krej = Int(25)
    interval_zscale_maxiterations = Int(5)

    interval_combobox_value = str
    stretch_combobox_value = str

    def __init__(self):
        # self.stretch_asinh_a = 2.5
        # self.stretch_contrast_contrast = 20
        # self.stretch_contrast_bias = 20
        # self.stretch_linear_slope = 10
        # self.stretch_linear_intercept = 1
        # self.stretch_log_a = 1
        # self.stretch_powerdist_a = 1
        # self.stretch_power_a = 1
        # self.stretch_sinh_a = 1
        #
        # self.interval_manual_vmin = 1
        # self.interval_manual_vmax = 1
        # self.interval_percentile_percentile = 1
        # self.interval_percentile_nsamples = 1
        # self.interval_asymetric_lpercentile = 1
        # self.interval_asymetric_upercentile = 1
        # self.interval_asymetric_nsamples = 1
        # self.interval_zscale_nsamples = 1000
        # self.interval_zscale_contrast = 50
        # self.interval_zscale_maxreject = 5
        # self.interval_zscale_minpixels = 5
        # self.interval_zscale_krej = 25
        # self.interval_zscale_maxiterations = 5
        #
        # x = dict(nsamples = interval_zscale_nsamples)
        self.observe(self.func, names=['stretch_asinh_a'])

    def func(self, change):
            print("SliderValue func")
            print(change['old'])
            print(change['new'])

    def checkVars(self):
        print("-------------------")
        print(self.stretch_asinh_a)
        print(self.stretch_contrast_contrast)
        print(self.stretch_contrast_bias)
        print(self.interval_zscale_contrast)
        print("-------------------")