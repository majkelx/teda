from traitlets import HasTraits, Int, Float


class SliderValue(HasTraits):
    stretch_asinh_a = Int(1)
    stretch_contrastbias_contrast = Int(20)
    stretch_contrastbias_bias = Int(10)
    stretch_linear_slope = Int(10)
    stretch_linear_intercept = Int(0)
    stretch_log_a = Int()
    stretch_powerdist_a = Int()
    stretch_power_a = Int()
    stretch_sinh_a = Int()

    interval_manual_vmin = Int()
    interval_manual_vmax = Int()
    interval_percentile_percentile = Int()
    interval_percentile_nsamples = Int()
    interval_asymetric_lower_percentile = Int()
    interval_asymetric_upper_percentile = Int()
    interval_asymetric_nsamples = Int()
    interval_zscale_nsamples = Int(100)
    interval_zscale_contrast = Int(10)
    interval_zscale_maxreject = Int(5)
    interval_zscale_minpixels = Int(5)
    interval_zscale_krej = Int(25)
    interval_zscale_maxiterations = Int(5)

    def __init__(self):
        self.observe(self.func, names=['stretch_asinh_a',
                                       'stretch_contrastbias_contrast',
                                       'stretch_contrastbias_bias',
                                       'stretch_linear_slope',
                                       'stretch_linear_intercept',
                                       'stretch_log_a',
                                       'stretch_powerdist_a',
                                       'stretch_power_a',
                                       'stretch_sinh_a',
                                       'interval_manual_vmin',
                                       'interval_manual_vmax',
                                       'interval_percentile_percentile',
                                       'interval_percentile_nsamples',
                                       'interval_asymetric_lower_percentile',
                                       'interval_asymetric_upper_percentile',
                                       'interval_asymetric_nsamples',
                                       'interval_zscale_nsamples',
                                       'interval_zscale_contrast',
                                       'interval_zscale_maxreject',
                                       'interval_zscale_minpixels',
                                       'interval_zscale_krej',
                                       'interval_zscale_maxiterations'])

        self.dictionary = {
            'asinh': {'a': self.stretch_asinh_a},
            'contrastbias': {'contrast': self.stretch_contrastbias_contrast,
                             'bias': self.stretch_contrastbias_bias},
            'histogram': {},
            'linear': {'slope': self.stretch_linear_slope,
                       'intercept': self.stretch_linear_intercept},
            'log': {'a': self.stretch_log_a},
            'powerdist': {'a': self.stretch_powerdist_a},
            'power': {'a': self.stretch_power_a},
            'sinh': {'a': self.stretch_sinh_a},
            'sqrt': {},
            'square': {},
            'minmax': {},
            'manual': {'vmin': self.interval_manual_vmin,
                       'vmax': self.interval_manual_vmax},
            'percentile': {'percentile': self.interval_percentile_percentile,
                           'n_samples': self.interval_percentile_nsamples},
            'asymetric': {'lower_percentile': self.interval_asymetric_lower_percentile,
                          'upper_percentile': self.interval_asymetric_upper_percentile,
                          'n_samples': self.interval_asymetric_nsamples},
            'zscale': {'nsamples': self.interval_zscale_nsamples,
                       'contrast': self.interval_zscale_contrast,
                       'max_reject': self.interval_zscale_maxreject,
                       'min_npixels': self.interval_zscale_minpixels,
                       'krej': self.interval_zscale_krej,
                       'max_iterations': self.interval_zscale_maxiterations}
        }

    def func(self, change):
            print("SliderValue func")
            print(change['old'])
            print(change['new'])
            self.update(self.dictionary, change.name, change.new)

    def checkVars(self):
        print("-----Check_Vars-----")
        print(self.stretch_asinh_a)
        print(self.interval_zscale_maxiterations)
        print(self.interval_zscale_nsamples)
        print(self.interval_zscale_contrast)
        print("--------END---------")

    def update(self, kw, args, value):
        print("Update")
        params = args.split("_")
        print(params)
        if params[1] == 'percentile' or params[1] == 'asymetric':
            if params[2] == 'nsamples':
                kw[params[1]]['n_samples'] = value
            else:
                kw[params[1]][params[2]] = value
        elif params[1] == 'zscale':
            if params[2] == 'maxreject':
                kw[params[1]]['max_reject'] = value
            if params[2] == 'minpixels':
                kw[params[1]]['mmin_npixels'] = value
            if params[2] == 'maxiterations':
                kw[params[1]]['max_iterations'] = value
            else:
                kw[params[1]][params[2]] = value
        else:
            kw[params[1]][params[2]] = value

