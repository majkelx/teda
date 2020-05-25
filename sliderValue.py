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

    def __init__(self):
        self.observe(self.func, names=['stretch_asinh_a','interval_zscale_contrast'])

        self.dictionary = {
            'zscale': {'contrast': self.interval_zscale_contrast}
        }

    def func(self, change):
            print("SliderValue func")
            print(change['old'])
            print(change['new'])
            self.update(self.dictionary)

    def checkVars(self):
        print("-----Check_Vars-----")
        print(self.stretch_asinh_a)
        print(self.interval_zscale_maxiterations)
        print(self.interval_zscale_nsamples)
        print(self.interval_zscale_contrast)
        print("--------END---------")

    def update(self, d):
        print("Update")
        d['zscale']['contrast'] = self.interval_zscale_contrast

