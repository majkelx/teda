from traitlets import HasTraits, Int, Float, Unicode


class ScalesModel(HasTraits):
    stretch_asinh_a = Float(0.1)
    stretch_contrastbias_contrast = Float(2.0)
    stretch_contrastbias_bias = Float(1.0)
    stretch_linear_slope = Float(1.0)
    stretch_linear_intercept = Float(0.0)
    stretch_log_a = Float(1000.0)
    stretch_powerdist_a = Float(1000.0)
    stretch_power_a = Float(1.0)
    stretch_sinh_a = Float(0.33)

    interval_manual_vmin = Float(0.0)
    interval_manual_vmax = Int(30000)
    interval_percentile_percentile = Float(0.1)
    interval_percentile_nsamples = Int(1000)
    interval_asymetric_lower_percentile = Float(0.1)
    interval_asymetric_upper_percentile = Float(0.2)
    interval_asymetric_nsamples = Int(1000)
    interval_zscale_nsamples = Int(1000)
    interval_zscale_contrast = Float(0.25)
    interval_zscale_maxreject = Float(0.5)
    interval_zscale_minpixels = Int(5)
    interval_zscale_krej = Float(2.5)
    interval_zscale_maxiterations = Int(5)

    selected_stretch = Unicode('linear')
    selected_interval = Unicode('zscale')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            'sqrt': {},
            'square': {},
            'minmax': {},
            'histogram': {},
            'asinh': {'a': self.stretch_asinh_a},
            'contrastbias': {'contrast': self.stretch_contrastbias_contrast,
                             'bias': self.stretch_contrastbias_bias},
            'linear': {'slope': self.stretch_linear_slope,
                       'intercept': self.stretch_linear_intercept},
            'log': {'a': self.stretch_log_a},
            'powerdist': {'a': self.stretch_powerdist_a},
            'power': {'a': self.stretch_power_a},
            'sinh': {'a': self.stretch_sinh_a},

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
            self.update(self.dictionary, change.name, change.new)

    def update(self, kw, args, value):
        params = args.split("_")
        if params[1] == 'percentile':
            if params[2] != 'nsamples':
                kw[params[1]][params[2]] = value
            else:
                kw[params[1]]['n_samples'] = value
        elif params[1] == 'asymetric':
            if params[2] == 'upper':
                kw[params[1]]['upper_percentile'] = value
            elif params[2] == 'lower':
                kw[params[1]]['lower_percentile'] = value
            elif params[2] == 'nsamples':
                kw[params[1]]['n_samples'] = value
            else:
                kw[params[1]][params[2]] = value
        elif params[1] == 'zscale':
            if params[2] == 'maxreject':
                kw[params[1]]['max_reject'] = value
            elif params[2] == 'minpixels':
                kw[params[1]]['min_npixels'] = value
            elif params[2] == 'maxiterations':
                kw[params[1]]['max_iterations'] = value
            else:
                kw[params[1]][params[2]] = value
        else:
            kw[params[1]][params[2]] = value


