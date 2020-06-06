
from PySide2.QtCore import Qt, QSettings
from PySide2.QtWidgets import (QLabel, QSlider, QStackedLayout, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QComboBox)
from traitlets import TraitError

class ScaleWidget(QWidget):
    stretches_list = ['powerdist', 'asinh', 'contrastbias', 'histogram', 'linear',
     'log', 'power', 'sinh', 'sqrt', 'square']
    intervals_list = ['zscale','minmax', 'manual', 'percentile', 'asymetric']


    def __init__(self, parent, scales_model, cmap_model):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.scalesModel = scales_model
        self.cmapModel = cmap_model
        self.ignore_signals = False

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

        self.adjustCombos()
        self.adjustCmapCombo()
        self.adjustSliders()

        self.scalesModel.observe(lambda change: self.onScaleModelChange(change))
        self.cmapModel.observe(lambda change: self.onCmapModelChange(change))

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
        self.manual_vmin.setMaximum(30000)
        self.manual_vmin.setSingleStep(100)

        self.manual_vmax = QSlider(Qt.Horizontal)
        self.manual_vmax.setMinimum(10000)
        self.manual_vmax.setMaximum(60000)
        self.manual_vmax.setSingleStep(100)

        self.manual_vmin.valueChanged.connect(lambda changed: self.onSliderChange('interval_manual_vmin',
                                                                                  self.manual_vmin.value() / 10.0))
        self.manual_vmax.valueChanged.connect(lambda changed: self.onSliderChange('interval_manual_vmax',
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

        self.percentile_percentile.valueChanged.connect(lambda changed: self.onSliderChange('interval_percentile_percentile',
                                                                                            self.percentile_percentile.value() / 10.0))
        self.percentile_nsamples.valueChanged.connect(lambda changed: self.onSliderChange('interval_percentile_nsamples',
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

        self.asymetric_lpercentile.valueChanged.connect(lambda changed: self.onSliderChange('interval_asymetric_lower_percentile',
                                                                                            self.asymetric_lpercentile.value() / 10.0))
        self.asymetric_upercentile.valueChanged.connect(lambda changed: self.onSliderChange('interval_asymetric_upper_percentile',
                                                                                            self.asymetric_upercentile.value() / 10.0))
        self.asymetric_nsamples.valueChanged.connect(lambda changed: self.onSliderChange('interval_asymetric_nsamples',
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

        self.zscale_nsamples.valueChanged.connect(lambda changed: self.onSliderChange('interval_zscale_nsamples',
                                                                                      self.zscale_nsamples.value()))
        self.zscale_contrast.valueChanged.connect(lambda changed: self.onSliderChange('interval_zscale_contrast',
                                                                                      self.zscale_contrast.value() / 100.0))
        self.zscale_mreject.valueChanged.connect(lambda changed: self.onSliderChange('interval_zscale_maxreject',
                                                                                     self.zscale_mreject.value() / 10))
        self.zscale_minpixels.valueChanged.connect(lambda changed: self.onSliderChange('interval_zscale_minpixels',
                                                                                       self.zscale_minpixels.value()))
        self.zscale_krej.valueChanged.connect(lambda changed: self.onSliderChange('interval_zscale_krej',
                                                                                  self.zscale_krej.value() / 10))
        self.zscale_miterations.valueChanged.connect(lambda changed: self.onSliderChange('interval_zscale_maxiterations',
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
        self.stretch_combobox.addItems(self.stretches_list)


        self.interval_combobox = QComboBox()
        self.interval_combobox.setFocusPolicy(Qt.NoFocus)
        self.interval_combobox.addItems(self.intervals_list)

        self.color_combobox = QComboBox()
        self.color_combobox.setFocusPolicy(Qt.NoFocus)
        self.color_combobox.addItems(self.cmapModel.colormaps.keys())
        self.color_combobox.setCurrentText(self.cmapModel.cmap_idx)

        layout.addWidget(self.stretch_combobox)
        layout.addWidget(self.interval_combobox)
        layout.addWidget(self.color_combobox)

        self.stretch_combobox.activated.connect(lambda activated: self.on_select_stretch())
        self.interval_combobox.activated.connect(lambda activated: self.on_select_interval())
        self.color_combobox.activated.connect(lambda activated: self.on_select_cmap())
        return layout


    # For functionalty below, see FitsPlotterControlled.scale_from_model()
    # def fitsNormalization(self, stretch, interval):
    #     self.parent.fits_image.set_normalization(stretch=stretch,
    #                                       interval=interval,
    #                                       stretchkwargs=self.scalesModel.dictionary[stretch],
    #                                       intervalkwargs=self.scalesModel.dictionary[interval])
    #
    #     self.parent.fits_image.invalidate()
    #     self.parent.updateFitsInWidgets()

    def createAsinhParamsSliders(self):
        widget = QWidget()
        layout = QGridLayout()

        self.asinh_a = QSlider(Qt.Horizontal)
        self.asinh_a.setMinimum(1)
        self.asinh_a.setMaximum(10)

        self.asinh_a.valueChanged.connect(
            lambda changed: self.onSliderChange('stretch_asinh_a', self.asinh_a.value() / 10.0))
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
            lambda changed: self.onSliderChange('stretch_contrastbias_contrast',
                                                self.contrast_contrast.value() / 10.0))
        self.contrast_bias.valueChanged.connect(lambda changed: self.onSliderChange('stretch_contrastbias_bias',
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
        self.linear_slope.valueChanged.connect(lambda changed: self.onSliderChange('stretch_linear_slope',
                                                                                   self.linear_slope.value() / 10.0))
        self.linear_intercept.valueChanged.connect(lambda changed: self.onSliderChange('stretch_linear_intercept',
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

        self.log_a.valueChanged.connect(lambda changed: self.onSliderChange('stretch_log_a',
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

        self.powerdist_a.valueChanged.connect(lambda changed: self.onSliderChange('stretch_powerdist_a',
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

        self.power_a.valueChanged.connect(lambda changed: self.onSliderChange('stretch_power_a',
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

        self.sinh_a.valueChanged.connect(lambda changed: self.onSliderChange('stretch_sinh_a',
                                                                             self.sinh_a.value() / 100.0))

        layout.addWidget(QLabel('a'), 0, 0)
        layout.addWidget(self.sinh_a, 0, 1)
        widget.setLayout(layout)
        return widget

    def onSliderChange(self, param, value):
        if self.ignore_signals:
            return
        self.ignore_signals = True
        try:
            setattr(self.scalesModel, param, value)
        finally:
            self.ignore_signals = False
        # current_stretch = self.stretch_combobox.currentText()
        # current_interval = self.interval_combobox.currentText()
        #
        # self.fitsNormalization(current_stretch, current_interval)


    def onScaleModelChange(self, change):
        if self.ignore_signals:  # avoid selfupdate on moving sliders
            return
        self.adjustCombos()
        self.adjustSliders()

    def onCmapModelChange(self, change):
        self.adjustCmapCombo()

    def on_select_stretch(self):
        self.scalesModel.selected_stretch = self.stretch_combobox.currentText()

    def on_select_interval(self):
        self.scalesModel.selected_interval = self.interval_combobox.currentText()

    def on_select_cmap(self):
        self.cmapModel.cmap_idx = self.color_combobox.currentText()

    def adjustCombos(self):
        """Select layout page from model and set scale combos value"""
        self.stretch_combobox.setCurrentText(self.scalesModel.selected_stretch)
        self.interval_combobox.setCurrentText(self.scalesModel.selected_interval)
        try:
            self.stretchStackedLayout.setCurrentIndex(
                self.stretches_list.index(self.scalesModel.selected_stretch))
        except ValueError:
            pass
        try:
            self.intervalStackedLayout.setCurrentIndex(
                self.intervals_list.index(self.scalesModel.selected_interval))
        except ValueError:
            pass
        # self.fitsNormalization(self.stretch_combobox.currentText(), self.interval_combobox.currentText())

    def adjustCmapCombo(self):
        """Set combo value"""
        self.color_combobox.setCurrentText(self.cmapModel.cmap_idx)

    def adjustSliders(self):
        ignore_signals = self.ignore_signals
        self.ignore_signals = True
        try:
            # self.selectSliders(self.stretchStackedLayout.currentIndex(), self.intervalStackedLayout.currentIndex())
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
        finally:
            self.ignore_signals = ignore_signals


    def writeSlidersValues(self):
        # TODO: Move Save/Load settings to model object
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

        settings.setValue("cmap", self.cmapModel.cmap_idx)
        settings.setValue("stretch", self.scalesModel.selected_stretch)
        settings.setValue("interval", self.scalesModel.selected_interval)
        # settings.setValue("cmap", self.color_combobox.currentIndex())

        settings.endGroup()

    def readSlidersValues(self):
        settings = QSettings()
        settings.beginGroup("Sliders")

        self.setModelValue('cmap_idx', settings.value("cmap"), model=self.cmapModel)
        self.setModelValue('selected_stretch', settings.value("stretch"))
        self.setModelValue('selected_interval', settings.value("interval"))
        # self.color_combobox.setCurrentIndex(settings.value("cmap", 3))

        self.setModelValue('stretch_asinh_a', settings.value('asinh/a'))
        self.setModelValue('stretch_contrastbias_contrast', settings.value('contrast/contrast'))
        self.setModelValue('stretch_contrastbias_bias', settings.value('contrast/bias'))
        self.setModelValue('stretch_linear_slope', settings.value('linear/slope'))
        self.setModelValue('stretch_linear_intercept', settings.value('linear/intercept'))
        self.setModelValue('stretch_log_a', settings.value('log/a'))
        self.setModelValue('stretch_powerdist_a', settings.value('powerdist/a'))
        self.setModelValue('stretch_power_a', settings.value('power/a'))
        self.setModelValue('stretch_sinh_a', settings.value('sinh/a'))

        self.setModelValue('interval_manual_vmin', settings.value('manual/vmin'))
        self.setModelValue('interval_manual_vmax', settings.value('manual/vmax'))
        self.setModelValue('interval_percentile_percentile', settings.value('percentile/percentile'))
        self.setModelValue('interval_percentile_nsamples', settings.value('percentile/nsamples'))
        self.setModelValue('interval_asymetric_lower_percentile', settings.value('asymetric/lpercentile'))
        self.setModelValue('interval_asymetric_upper_percentile', settings.value('asymetric/upercentile'))
        self.setModelValue('interval_asymetric_nsamples', settings.value('asymetric/nsamples'))
        self.setModelValue('interval_zscale_nsamples', settings.value('zscale/nsamples'))
        self.setModelValue('interval_zscale_contrast', settings.value('zscale/contrast'))
        self.setModelValue('interval_zscale_maxreject', settings.value('zscale/maxreject'))
        self.setModelValue('interval_zscale_minpixels', settings.value('zscale/minpixels'))
        self.setModelValue('interval_zscale_krej', settings.value('zscale/krej'))
        self.setModelValue('interval_zscale_maxiterations', settings.value('zscale/maxiterations'))
        settings.endGroup()

    def setModelValue(self, model_key, value, model=None):
        if model is None:
            model = self.scalesModel
        try:
            setattr(model, model_key, value)
            pass
        except TraitError:
            if value is not None:
                print(f'Attempt to set {model_key} := {value} caused exception. Ignored')
