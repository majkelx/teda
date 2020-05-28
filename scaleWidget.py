
from PySide2.QtCore import Qt, QSettings
from PySide2.QtWidgets import (QLabel, QSlider, QStackedLayout, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QComboBox)
from scalesModel import (ScalesModel)

class ScaleWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.scalesModel = ScalesModel()

        # comboboxes
        layout = QVBoxLayout()
        self.combobox_widget = QWidget()
        self.combobox_widget.setEnabled(False)
        self.combobox_layout = self.createComboboxes()
        self.combobox_widget.setLayout(self.combobox_layout)
        # self.combobox_widget.setMaximumHeight(40)
        layout.addWidget(self.combobox_widget)

        # Stretch
        self.stretch_sliders_widget = QWidget()
        self.stretch_sliders_layout = self.createStretchStackedLayout()
        self.stretch_sliders_widget.setEnabled(False)
        self.stretch_sliders_widget.setLayout(self.stretch_sliders_layout)
        # self.stretch_sliders_widget.setMaximumHeight(50)
        layout.addWidget(self.stretch_sliders_widget)

        # Interval
        self.interval_sliders_widget = QWidget()
        self.interval_sliders_layout = self.createIntervalStackedLayout()
        self.interval_sliders_widget.setEnabled(False)
        self.interval_sliders_widget.setLayout(self.interval_sliders_layout)
        # self.interval_sliders_widget.setMaximumHeight(125)
        layout.addWidget(self.interval_sliders_widget)
        self.setLayout(layout)
        self.setMaximumHeight(350)

    def createStretchStackedLayout(self):
        self.stretchStackedLayout = QStackedLayout()
        asinh = self.createAsinhParamsSliders()
        contrastbias = self.createContrastbiasParamsSliders()
        histogram = QLabel("")
        linear = self.createLinearSliders()
        log = self.createLogSliders()
        powerdist = self.createPowerdistSliders()
        power = self.createPowerSliders()
        sinh = self.createSinhSliders()
        sqrt = QLabel("")
        square = QLabel("")
        self.stretchStackedLayout.addWidget(powerdist)
        self.stretchStackedLayout.addWidget(asinh)
        self.stretchStackedLayout.addWidget(contrastbias)
        self.stretchStackedLayout.addWidget(histogram)
        self.stretchStackedLayout.addWidget(linear)
        self.stretchStackedLayout.addWidget(log)
        self.stretchStackedLayout.addWidget(power)
        self.stretchStackedLayout.addWidget(sinh)
        self.stretchStackedLayout.addWidget(sqrt)
        self.stretchStackedLayout.addWidget(square)

        return self.stretchStackedLayout

    def createIntervalStackedLayout(self):
        self.intervalStackedLayout = QStackedLayout()

        manual = self.createManualParamsSliders()
        percentile = self.createPercentileParamsSliders()
        asymetric = self.createAsymetricParamsSliders()
        zscale = self.createZscaleParamsSliders()
        self.intervalStackedLayout.addWidget(zscale)
        self.intervalStackedLayout.addWidget(QLabel(""))
        self.intervalStackedLayout.addWidget(manual)
        self.intervalStackedLayout.addWidget(percentile)
        self.intervalStackedLayout.addWidget(asymetric)

        return self.intervalStackedLayout

    def createManualParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()
        self.manual_vmin = QSlider(Qt.Horizontal)
        self.manual_vmin.setMinimum(0)
        self.manual_vmin.setMaximum(10000)

        self.manual_vmax = QSlider(Qt.Horizontal)
        self.manual_vmax.setMinimum(10000)
        self.manual_vmax.setMaximum(50000)

        self.manual_vmin.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_manual_vmin',
                                                                                       self.manual_vmin.value() / 10.0))
        self.manual_vmax.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_manual_vmax',
                                                                                       self.manual_vmax.value()))

        layout.addWidget(QLabel('vmin'), 0, 0)
        layout.addWidget(self.manual_vmin, 0, 1)
        layout.addWidget(QLabel('vmax'), 1, 0)
        layout.addWidget(self.manual_vmax, 1, 1)
        widget.setLayout(layout)

        return widget

    def createPercentileParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()
        self.percentile_percentile = QSlider(Qt.Horizontal)
        self.percentile_percentile.setMinimum(1)
        self.percentile_percentile.setMaximum(10)

        self.percentile_nsamples = QSlider(Qt.Horizontal)
        self.percentile_nsamples.setMinimum(500)
        self.percentile_nsamples.setMaximum(1500)

        self.percentile_percentile.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_percentile_percentile',
                                                                                                 self.percentile_percentile.value() / 10.0))
        self.percentile_nsamples.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_percentile_nsamples',
                                                                                               self.percentile_nsamples.value()))

        layout.addWidget(QLabel('percentile'), 0, 0)
        layout.addWidget(self.percentile_percentile, 0, 1)
        layout.addWidget(QLabel('samples'), 1, 0)
        layout.addWidget(self.percentile_nsamples, 1, 1)
        widget.setLayout(layout)

        return widget

    def createAsymetricParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.asymetric_lpercentile = QSlider(Qt.Horizontal)
        self.asymetric_lpercentile.setMinimum(1)
        self.asymetric_lpercentile.setMaximum(10)

        self.asymetric_upercentile = QSlider(Qt.Horizontal)
        self.asymetric_upercentile.setMinimum(2)
        self.asymetric_upercentile.setMaximum(20)

        self.asymetric_nsamples = QSlider(Qt.Horizontal)
        self.asymetric_nsamples.setMinimum(500)
        self.asymetric_nsamples.setMaximum(1500)

        self.asymetric_lpercentile.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_asymetric_lower_percentile',
                                                                                                 self.asymetric_lpercentile.value() / 10.0))
        self.asymetric_upercentile.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_asymetric_upper_percentile',
                                                                                                 self.asymetric_upercentile.value() / 10.0))
        self.asymetric_nsamples.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_asymetric_nsamples',
                                                                                              self.asymetric_nsamples.value()))

        layout.addWidget(QLabel("l_percentile"), 0, 0)
        layout.addWidget(self.asymetric_lpercentile, 0, 1)
        layout.addWidget(QLabel("u_percentile"), 1, 0)
        layout.addWidget(self.asymetric_upercentile, 1, 1)
        layout.addWidget(QLabel("samples"), 2, 0)
        layout.addWidget(self.asymetric_nsamples, 2, 1)
        widget.setLayout(layout)

        return widget

    def createZscaleParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.zscale_nsamples = QSlider(Qt.Horizontal)
        self.zscale_nsamples.setMinimum(500)
        self.zscale_nsamples.setMaximum(1500)

        self.zscale_contrast = QSlider(Qt.Horizontal)
        self.zscale_contrast.setMinimum(10)
        self.zscale_contrast.setMaximum(50)

        self.zscale_mreject = QSlider(Qt.Horizontal)
        self.zscale_mreject.setMinimum(1)
        self.zscale_mreject.setMaximum(20)

        self.zscale_minpixels = QSlider(Qt.Horizontal)
        self.zscale_minpixels.setMinimum(1)
        self.zscale_minpixels.setMaximum(10)

        self.zscale_krej = QSlider(Qt.Horizontal)
        self.zscale_krej.setMinimum(10)
        self.zscale_krej.setMaximum(50)

        self.zscale_miterations = QSlider(Qt.Horizontal)
        self.zscale_miterations.setMinimum(1)
        self.zscale_miterations.setMaximum(10)

        self.zscale_nsamples.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_nsamples',
                                                                                           self.zscale_nsamples.value()))
        self.zscale_contrast.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_contrast',
                                                                                           self.zscale_contrast.value() / 100.0))
        self.zscale_mreject.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_maxreject',
                                                                                          self.zscale_mreject.value() / 10))
        self.zscale_minpixels.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_minpixels',
                                                                                            self.zscale_minpixels.value()))
        self.zscale_krej.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_krej',
                                                                                       self.zscale_krej.value() / 10))
        self.zscale_miterations.valueChanged.connect(lambda changed: self.changeSlidersParams('interval_zscale_maxiterations',
                                                                                              self.zscale_miterations.value()))

        layout.addWidget(QLabel("samples"), 0, 0)
        layout.addWidget(self.zscale_nsamples, 0, 1)
        layout.addWidget(QLabel("contrast"), 1, 0)
        layout.addWidget(self.zscale_contrast, 1, 1)
        layout.addWidget(QLabel("max reject"), 2, 0)
        layout.addWidget(self.zscale_mreject, 2, 1)
        layout.addWidget(QLabel("pixels"), 3, 0)
        layout.addWidget(self.zscale_minpixels, 3, 1)
        layout.addWidget(QLabel("krej"), 4, 0)
        layout.addWidget(self.zscale_krej, 4, 1)
        layout.addWidget(QLabel("m_iterations"), 5, 0)
        layout.addWidget(self.zscale_miterations, 5, 1)

        widget.setLayout(layout)

        return widget

    def createComboboxes(self):
        layout = QHBoxLayout()

        self.stretch_combobox = QComboBox()
        self.stretch_combobox.setFocusPolicy(Qt.NoFocus)
        self.stretch_combobox.addItems(['powerdist', 'asinh', 'contrastbias', 'histogram', 'linear',
                                        'log', 'power', 'sinh', 'sqrt', 'square'])


        self.interval_combobox = QComboBox()
        self.interval_combobox.setFocusPolicy(Qt.NoFocus)
        self.interval_combobox.addItems(['zscale','minmax', 'manual', 'percentile', 'asymetric'])

        self.color_combobox = QComboBox()
        self.color_combobox.setFocusPolicy(Qt.NoFocus)
        self.color_combobox.addItems(self.parent.cmaps.colormaps.keys())

        layout.addWidget(self.stretch_combobox)
        layout.addWidget(self.interval_combobox)
        layout.addWidget(self.color_combobox)

        self.stretch_combobox.activated.connect(lambda activated: self.getSliders(self.stretch_combobox.currentIndex(), self.interval_combobox.currentIndex()))
        self.interval_combobox.activated.connect(lambda activated: self.getSliders(self.stretch_combobox.currentIndex(), self.interval_combobox.currentIndex()))
        self.color_combobox.currentTextChanged.connect(lambda activated: self.parent.changeColor(self.color_combobox.currentText()))
        return layout

    def getSliders(self, stretch_index, interval_index):
        self.stretchStackedLayout.setCurrentIndex(stretch_index)
        self.intervalStackedLayout.setCurrentIndex(interval_index)
        self.fitsNormalization(self.stretch_combobox.currentText(), self.interval_combobox.currentText())

    def fitsNormalization(self, stretch, interval):
        self.parent.fits_image.set_normalization(stretch=stretch,
                                          interval=interval,
                                          stretchkwargs=self.scalesModel.dictionary[stretch],
                                          intervalkwargs=self.scalesModel.dictionary[interval])

        self.parent.fits_image.invalidate()
        self.parent.updateFitsInWidgets()

    def changeSlidersParams(self, param, value):
        setattr(self.scalesModel, param, value)
        current_stretch = self.stretch_combobox.currentText()
        current_interval = self.interval_combobox.currentText()

        self.fitsNormalization(current_stretch, current_interval)

    def createAsinhParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.asinh_a = QSlider(Qt.Horizontal)
        self.asinh_a.setMinimum(1)
        self.asinh_a.setMaximum(10)

        self.asinh_a.valueChanged.connect(
            lambda changed: self.changeSlidersParams('stretch_asinh_a', self.asinh_a.value() / 10.0))
        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.asinh_a, 0, 1)
        widget.setLayout(layout)

        return widget

    def createContrastbiasParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.contrast_contrast = QSlider(Qt.Horizontal)
        self.contrast_contrast.setMinimum(1)
        self.contrast_contrast.setMaximum(30)

        self.contrast_bias = QSlider(Qt.Horizontal)
        self.contrast_bias.setMinimum(1)
        self.contrast_bias.setMaximum(20)

        self.contrast_contrast.valueChanged.connect(
            lambda changed: self.changeSlidersParams('stretch_contrastbias_contrast',
                                                     self.contrast_contrast.value() / 10.0))
        self.contrast_bias.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_contrastbias_bias',
                                                                                         self.contrast_bias.value() / 10.0))
        layout.addWidget(QLabel('contrast'), 0, 0)
        layout.addWidget(self.contrast_contrast, 0, 1)
        layout.addWidget(QLabel('bias'), 1, 0)
        layout.addWidget(self.contrast_bias, 1, 1)

        widget.setLayout(layout)

        return widget

    def createLinearSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.linear_slope = QSlider(Qt.Horizontal)
        self.linear_slope.setTickPosition(QSlider.TicksAbove)
        self.linear_slope.setMinimum(1)  # 0.1
        self.linear_slope.setMaximum(30)  # 3.0

        self.linear_intercept = QSlider(Qt.Horizontal)
        self.linear_intercept.setMinimum(-10)  # -1.0
        self.linear_intercept.setMaximum(10)  # 1.0

        # connects
        self.linear_slope.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_linear_slope',
                                                                                        self.linear_slope.value() / 10.0))
        self.linear_intercept.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_linear_intercept',
                                                                                            self.linear_intercept.value() / 10.0))

        layout.addWidget(QLabel("slope"), 0, 0)
        layout.addWidget(self.linear_slope, 0, 1)
        layout.addWidget(QLabel("intercept"), 1, 0)
        layout.addWidget(self.linear_intercept, 1, 1)

        widget.setLayout(layout)

        return widget

    def createLogSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.log_a = QSlider(Qt.Horizontal)
        self.log_a.setMinimum(5000)
        self.log_a.setMaximum(15000)

        self.log_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_log_a',
                                                                                 self.log_a.value() / 10.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.log_a, 0, 1)
        widget.setLayout(layout)

        return widget

    def createPowerdistSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.powerdist_a = QSlider(Qt.Horizontal)
        self.powerdist_a.setMinimum(5000)
        self.powerdist_a.setMaximum(15000)

        self.powerdist_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_powerdist_a',
                                                                                       self.powerdist_a.value() / 10.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.powerdist_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def createPowerSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.power_a = QSlider(Qt.Horizontal)
        self.power_a.setMinimum(1)
        self.power_a.setMaximum(20)

        self.power_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_power_a',
                                                                                   self.power_a.value() / 10.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.power_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def createSinhSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.sinh_a = QSlider(Qt.Horizontal)
        self.sinh_a.setMinimum(10)
        self.sinh_a.setMaximum(100)

        self.sinh_a.valueChanged.connect(lambda changed: self.changeSlidersParams('stretch_sinh_a',
                                                                                  self.sinh_a.value() / 100.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.sinh_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def adjustSliders(self):
        self.getSliders(self.stretchStackedLayout.currentIndex(), self.intervalStackedLayout.currentIndex())
        self.stretch_sliders_widget.setEnabled(True)
        self.interval_sliders_widget.setEnabled(True)
        self.combobox_widget.setEnabled(True)
        self.manual_vmin.setValue(self.scalesModel.interval_manual_vmin * 10)
        self.manual_vmax.setValue(self.scalesModel.interval_manual_vmax)
        self.percentile_percentile.setValue(self.scalesModel.interval_percentile_percentile * 10)
        self.percentile_nsamples.setValue(self.scalesModel.interval_percentile_nsamples)
        self.asymetric_lpercentile.setValue(self.scalesModel.interval_asymetric_lower_percentile * 10)
        self.asymetric_upercentile.setValue(self.scalesModel.interval_asymetric_upper_percentile * 10)
        self.asymetric_nsamples.setValue(self.scalesModel.interval_asymetric_nsamples)
        self.zscale_nsamples.setValue(self.scalesModel.interval_zscale_nsamples)
        self.zscale_contrast.setValue(self.scalesModel.interval_zscale_contrast * 100)
        self.zscale_mreject.setValue(self.scalesModel.interval_zscale_maxreject * 10)
        self.zscale_minpixels.setValue(self.scalesModel.interval_zscale_minpixels)
        self.zscale_krej.setValue(self.scalesModel.interval_zscale_krej * 10)
        self.zscale_miterations.setValue(self.scalesModel.interval_zscale_maxiterations)
        self.asinh_a.setValue(self.scalesModel.stretch_asinh_a * 10)
        self.contrast_contrast.setValue(self.scalesModel.stretch_contrastbias_contrast * 10)
        self.contrast_bias.setValue(self.scalesModel.stretch_contrastbias_bias * 10)
        self.linear_slope.setValue(self.scalesModel.stretch_linear_slope * 10)
        self.linear_intercept.setValue(self.scalesModel.stretch_linear_intercept * 10)
        self.log_a.setValue(self.scalesModel.stretch_log_a * 10)
        self.powerdist_a.setValue(self.scalesModel.stretch_powerdist_a * 10)
        self.power_a.setValue(self.scalesModel.stretch_power_a * 10)
        self.sinh_a.setValue(self.scalesModel.stretch_sinh_a * 100)

    def writeSlidersValues(self):
        settings = QSettings()
        settings.beginGroup("Sliders")
        settings.setValue("asinh/a", self.scalesModel.stretch_asinh_a)
        settings.setValue("contrast/contrast", self.scalesModel.stretch_contrastbias_contrast)
        settings.setValue("contrast/bias", self.scalesModel.stretch_contrastbias_bias)
        settings.setValue("linear/slope", self.scalesModel.stretch_linear_slope)
        settings.setValue("linear/intercept", self.scalesModel.stretch_linear_intercept)
        settings.setValue("log/a", self.scalesModel.stretch_log_a)
        settings.setValue("powerdist/a", self.scalesModel.stretch_powerdist_a)
        settings.setValue("power/a", self.scalesModel.stretch_power_a)
        settings.setValue("sinh/a", self.scalesModel.stretch_sinh_a)

        settings.setValue("manual/vmin", self.scalesModel.interval_manual_vmin)
        settings.setValue("manual/vmax", self.scalesModel.interval_manual_vmax)
        settings.setValue("percentile/percentile", self.scalesModel.interval_percentile_percentile)
        settings.setValue("percentile/nsamples", self.scalesModel.interval_percentile_nsamples)
        settings.setValue("asymetric/lpercentile", self.scalesModel.interval_asymetric_lower_percentile)
        settings.setValue("asymetric/upercentile", self.scalesModel.interval_asymetric_upper_percentile)
        settings.setValue("asymetric/nsamples", self.scalesModel.interval_asymetric_nsamples)
        settings.setValue("zscale/contrast", self.scalesModel.interval_zscale_contrast)
        settings.setValue("zscale/nsamples", self.scalesModel.interval_zscale_nsamples)
        settings.setValue("zscale/maxreject", self.scalesModel.interval_zscale_maxreject)
        settings.setValue("zscale/minpixels", self.scalesModel.interval_zscale_minpixels)
        settings.setValue("zscale/krej", self.scalesModel.interval_zscale_krej)
        settings.setValue("zscale/maxiterations", self.scalesModel.interval_zscale_maxiterations)

        settings.endGroup()

    def readSlidersValues(self):
        settings = QSettings()
        settings.beginGroup("Sliders")

        asinh_a_value = settings.value("asinh/a")
        contrast_contrast_value = settings.value("contrast/contrast")
        contrast_bias_value = settings.value("contrast/bias")
        linear_slope_value = settings.value("linear/slope")
        linear_intercept_value = settings.value("linear/intercept")
        log_a_value = settings.value("log/a")
        powerdist_a_value = settings.value("powerdist/a")
        power_a_value = settings.value("power/a")
        sinh_a_value = settings.value("sinh/a")

        manual_vmin_value = settings.value("manual/vmin")
        manual_vmax_value = settings.value("manual/vmax")
        percentile_percentile_value = settings.value("percentile/percentile")
        percentile_nsamples_value = settings.value("percentile/nsamples")
        asymetric_lpercentile_value = settings.value("asymetric/lpercentile")
        asymetric_upercentile_value = settings.value("asymetric/upercentile")
        asymetric_nsamples_value = settings.value("asymetric/nsamples")
        zscale_contrast_value = settings.value("zscale/contrast")
        zscale_nsamples_value = settings.value("zscale/nsamples")
        zscale_maxreject_value = settings.value("zscale/maxreject")
        zscale_minpixels_value = settings.value("zscale/minpixels")
        zscale_krej_value = settings.value("zscale/krej")
        zscale_maxiterations_value = settings.value("zscale/maxiterations")
        settings.endGroup()

        if asinh_a_value:
            self.scalesModel.stretch_asinh_a = float(asinh_a_value)
        if contrast_contrast_value:
            self.scalesModel.stretch_contrastbias_contrast = float(contrast_contrast_value)
        if contrast_bias_value:
            self.scalesModel.stretch_contrastbias_bias = float(contrast_bias_value)
        if linear_slope_value:
            self.scalesModel.stretch_linear_slope = float(linear_slope_value)
        if linear_intercept_value:
            self.scalesModel.stretch_linear_intercept = float(linear_intercept_value)
        if log_a_value:
            self.scalesModel.stretch_log_a = float(log_a_value)
        if powerdist_a_value:
            self.scalesModel.stretch_powerdist_a = float(powerdist_a_value)
        if power_a_value:
            self.scalesModel.stretch_power_a = float(power_a_value)
        if sinh_a_value:
            self.scalesModel.stretch_sinh_a = float(sinh_a_value)

        if manual_vmin_value:
            self.scalesModel.interval_manual_vmin = float(manual_vmin_value)
        if manual_vmax_value:
            self.scalesModel.interval_manual_vmax = int(manual_vmax_value)
        if percentile_percentile_value:
            self.scalesModel.interval_percentile_percentile = float(percentile_percentile_value)
        if percentile_nsamples_value:
            self.scalesModel.interval_percentile_nsamples = int(percentile_nsamples_value)
        if asymetric_lpercentile_value:
            self.scalesModel.interval_asymetric_lower_percentile = float(asymetric_lpercentile_value)
        if asymetric_upercentile_value:
            self.scalesModel.interval_asymetric_upper_percentile = float(asymetric_upercentile_value)
        if asymetric_nsamples_value:
            self.scalesModel.interval_asymetric_nsamples = int(asymetric_nsamples_value)
        if zscale_nsamples_value:
            self.scalesModel.interval_zscale_nsamples = int(zscale_nsamples_value)
        if zscale_contrast_value:
            self.scalesModel.interval_zscale_contrast = float(zscale_contrast_value)
        if zscale_maxreject_value:
            self.scalesModel.interval_zscale_maxreject = float(zscale_maxreject_value)
        if zscale_minpixels_value:
            self.scalesModel.interval_zscale_minpixels = int(zscale_minpixels_value)
        if zscale_krej_value:
            self.scalesModel.interval_zscale_krej = float(zscale_krej_value)
        if zscale_maxiterations_value:
            self.scalesModel.interval_zscale_maxiterations = int(zscale_maxiterations_value)