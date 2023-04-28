from PySide6.QtCore import Qt, QSettings, Slot, QSize
from PySide6.QtWidgets import (QLabel, QSlider, QStackedLayout, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
                               QComboBox, QFormLayout, QLineEdit, QSizePolicy, QLayout, QCheckBox)
from traitlets import TraitError
from .slider import IntSlider, FloatSlider, LabeledSlider


class ScaleWidget(QWidget):
    stretches_list = ['powerdist', 'asinh', 'contrastbias', 'histogram', 'linear',
                      'log', 'power', 'sinh', 'sqrt', 'square']
    intervals_list = ['zscale', 'minmax', 'manual', 'percentile', 'asymetric']

    def __init__(self, parent, scales_model, cmap_model):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.scalesModel = scales_model
        self.cmapModel = cmap_model
        self.ignore_signals = False
        layout = QVBoxLayout()
        layout.setSpacing(0)

        # pernament linear stretch
        self.perm_linear_widget = self.createLinearSliders()
        layout.addWidget(QLabel('Linear'))
        layout.addWidget(self.perm_linear_widget)

        # comboboxes
        self.combobox_widget = QWidget()
        self.combobox_layout = self.createComboboxes()
        self.combobox_widget.setLayout(self.combobox_layout)
        layout.addWidget(self.combobox_widget)

        # Stretch
        self.stretch_sliders_widget = QWidget()
        self.stretch_sliders_layout = self.createStretchStackedLayout()
        self.stretch_sliders_widget.setLayout(self.stretch_sliders_layout)
        layout.addWidget(self.stretch_sliders_widget)

        # Interval
        self.interval_sliders_widget = QWidget()
        self.interval_sliders_layout = self.createIntervalStackedLayout()
        self.interval_sliders_widget.setLayout(self.interval_sliders_layout)
        layout.addWidget(self.interval_sliders_widget)

        self.setLayout(layout)

        self.adjustCombos()
        self.adjustCmapCombo()
        self.adjustSliders()

        self.scalesModel.observe(lambda change: self.onScaleModelChange(change))
        self.cmapModel.observe(lambda change: self.onCmapModelChange(change))

    def createStretchStackedLayout(self):
        self.stretchStackedLayout = QStackedLayout()
        asinh = self.createAsinhParamsSliders()
        contrastbias = self.createContrastbiasParamsSliders()
        histogram = QLabel('')
        linear = QLabel('')
        log = self.createLogSliders()
        powerdist = self.createPowerdistSliders()
        power = self.createPowerSliders()
        sinh = self.createSinhSliders()
        sqrt = QLabel('')
        square = QLabel('')
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
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.manual_vmin = FloatSlider(min=0.0, max=30000.0)
        self.manual_vmax = IntSlider(min=0, max=30000)

        self.manual_vmin.valueChanged.connect(lambda val=vars: self.onSliderChange('interval_manual_vmin', val))
        self.manual_vmax.valueChanged.connect(lambda val=vars: self.onSliderChange('interval_manual_vmax', val))

        layout.addRow('vmin', self.manual_vmin)
        layout.addRow('vmax', self.manual_vmax)
        widget.setLayout(layout)

        return widget

    def createPercentileParamsSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.percentile_percentile = FloatSlider(min=0.1, max=2.0)
        self.percentile_nsamples = IntSlider(min=1, max=2000)

        self.percentile_percentile.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_percentile_percentile', val))
        self.percentile_nsamples.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_percentile_nsamples', val))

        layout.addRow('percentile', self.percentile_percentile)
        layout.addRow('samples', self.percentile_nsamples)
        widget.setLayout(layout)

        return widget

    def createAsymetricParamsSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.asymetric_lpercentile = FloatSlider(min=0.0, max=2.0)
        self.asymetric_upercentile = FloatSlider(min=0.0, max=2.0)
        self.asymetric_nsamples = IntSlider(min=0, max=2000)

        self.asymetric_lpercentile.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_asymetric_lower_percentile', val))
        self.asymetric_upercentile.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_asymetric_upper_percentile', val))
        self.asymetric_nsamples.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_asymetric_nsamples', val))

        layout.addRow("l_percentile", self.asymetric_lpercentile)
        layout.addRow("u_percentile", self.asymetric_upercentile)
        layout.addRow("samples", self.asymetric_nsamples)

        widget.setLayout(layout)
        widget.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        return widget

    def createZscaleParamsSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.zscale_nsamples = IntSlider(min=0, max=2000)
        self.zscale_contrast = FloatSlider(min=0.0, max=2.0)
        self.zscale_mreject = FloatSlider(min=0.0, max=2.0)
        self.zscale_minpixels = IntSlider(min=0.0, max=20)
        self.zscale_krej = FloatSlider(min=0.0, max=5.0)
        self.zscale_miterations = IntSlider(min=0, max=20)

        self.zscale_nsamples.valueChanged.connect(lambda val=vars: self.onSliderChange('interval_zscale_nsamples', val))
        self.zscale_contrast.valueChanged.connect(lambda val=vars: self.onSliderChange('interval_zscale_contrast', val))
        self.zscale_mreject.valueChanged.connect(lambda val=vars: self.onSliderChange('interval_zscale_maxreject', val))
        self.zscale_minpixels.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_zscale_minpixels', val))
        self.zscale_krej.valueChanged.connect(lambda val=vars: self.onSliderChange('interval_zscale_krej', val))
        self.zscale_miterations.valueChanged.connect(
            lambda val=vars: self.onSliderChange('interval_zscale_maxiterations', val))

        layout.addRow("samples", self.zscale_nsamples)
        layout.addRow("contrast", self.zscale_contrast)
        layout.addRow("max reject", self.zscale_mreject)
        layout.addRow("pixels", self.zscale_minpixels)
        layout.addRow("krej", self.zscale_krej)
        layout.addRow("m_iterations", self.zscale_miterations)

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
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.asinh_a = FloatSlider(min=0.1, max=2.0)
        self.asinh_a.valueChanged.connect(
            lambda val=vars: self.onSliderChange('stretch_asinh_a', val))

        layout.addRow('a', self.asinh_a)
        widget.setLayout(layout)

        return widget

    def createContrastbiasParamsSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.contrast_contrast = FloatSlider(min=0.0, max=4.0)
        self.contrast_bias = FloatSlider(min=0.0, max=2.0)

        self.contrast_contrast.valueChanged.connect(
            lambda val=vars: self.onSliderChange('stretch_contrastbias_contrast', val))
        self.contrast_bias.valueChanged.connect(lambda val=vars: self.onSliderChange('stretch_contrastbias_bias', val))

        layout.addRow('contrast', self.contrast_contrast)
        layout.addRow('bias', self.contrast_bias)
        widget.setLayout(layout)

        return widget

    def createLinearSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.linear_slope = FloatSlider(min=0.1, max=3.0)
        self.linear_intercept = FloatSlider(min=-1.0, max=1.0)

        self.linear_slope.valueChanged.connect(lambda val=vars: self.onSliderChange('stretch_linear_slope', val))
        self.linear_intercept.valueChanged.connect(
            lambda val=vars: self.onSliderChange('stretch_linear_intercept', val))

        layout.addRow('slope', self.linear_slope)
        layout.addRow('intercept', self.linear_intercept)
        widget.setLayout(layout)

        return widget

    def createLogSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.log_a = FloatSlider(min=0.1, max=2000.0)
        self.log_a.valueChanged.connect(lambda val=vars: self.onSliderChange('stretch_log_a', val))

        layout.addRow('a', self.log_a)
        widget.setLayout(layout)

        return widget

    def createPowerdistSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.powerdist_a = FloatSlider(min=10.0, max=2000.0)
        self.powerdist_a.valueChanged.connect(lambda val=vars: self.onSliderChange('stretch_powerdist_a', val))

        layout.addRow('a', self.powerdist_a)
        widget.setLayout(layout)

        return widget

    def createPowerSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.power_a = FloatSlider(min=0.1, max=2.0)
        self.power_a.valueChanged.connect(lambda val=vars: self.onSliderChange('stretch_power_a', val))

        layout.addRow('a', self.power_a)
        widget.setLayout(layout)

        return widget

    def createSinhSliders(self):
        widget = QWidget()
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        self.sinh_a = FloatSlider(min=0.1, max=1.0)
        self.sinh_a.valueChanged.connect(lambda val=vars: self.onSliderChange('stretch_sinh_a', val))

        layout.addRow('a', self.sinh_a)
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
        try:
            self.adjustWidgetHeight(self.scalesModel.selected_stretch, self.scalesModel.selected_interval)
        except ValueError:
            pass

        # self.fitsNormalization(self.stretch_combobox.currentText(), self.interval_combobox.currentText())

    def adjustWidgetHeight(self, stretch, interval):
        self.perm_linear_widget.setMaximumHeight(100)
        self.combobox_widget.setMaximumHeight(40)

        widget_height = 160
        if stretch == 'linear' or stretch == 'histogram' or stretch == 'sqrt' or stretch == 'square':
            self.stretch_sliders_widget.hide()
        else:
            self.stretch_sliders_widget.show()
            if stretch == 'contrastbias' or stretch == 'linear':
                widget_height = widget_height + 100
                self.stretch_sliders_widget.setMaximumHeight(100)
            else:
                widget_height = widget_height + 50
                self.stretch_sliders_widget.setMaximumHeight(50)

        if interval == 'minmax':
            self.interval_sliders_widget.hide()
        else:
            self.interval_sliders_widget.show()
            if interval == 'asymetric':
                widget_height = widget_height + 120
                self.interval_sliders_widget.setMaximumHeight(120)
            elif interval == 'zscale':
                widget_height = widget_height + 210
                self.interval_sliders_widget.setMaximumHeight(210)
            else:
                widget_height = widget_height + 80
                self.interval_sliders_widget.setMaximumHeight(80)

        self.setMaximumHeight(widget_height)

    def adjustCmapCombo(self):
        """Set combo value"""
        self.color_combobox.setCurrentText(self.cmapModel.cmap_idx)

    def adjustSliders(self):
        ignore_signals = self.ignore_signals
        self.ignore_signals = True
        try:
            self.manual_vmin.set_value_from_settings(self.scalesModel.interval_manual_vmin)
            self.manual_vmax.set_value_from_settings(self.scalesModel.interval_manual_vmax)
            self.percentile_percentile.set_value_from_settings(self.scalesModel.interval_percentile_percentile)
            self.percentile_nsamples.set_value_from_settings(self.scalesModel.interval_percentile_nsamples)
            self.asymetric_lpercentile.set_value_from_settings(self.scalesModel.interval_asymetric_lower_percentile)
            self.asymetric_upercentile.set_value_from_settings(self.scalesModel.interval_asymetric_upper_percentile)
            self.asymetric_nsamples.set_value_from_settings(self.scalesModel.interval_asymetric_nsamples)
            self.zscale_nsamples.set_value_from_settings(self.scalesModel.interval_zscale_nsamples)
            self.zscale_contrast.set_value_from_settings(self.scalesModel.interval_zscale_contrast)
            self.zscale_mreject.set_value_from_settings(self.scalesModel.interval_zscale_maxreject)
            self.zscale_minpixels.set_value_from_settings(self.scalesModel.interval_zscale_minpixels)
            self.zscale_krej.set_value_from_settings(self.scalesModel.interval_zscale_krej)
            self.zscale_miterations.set_value_from_settings(self.scalesModel.interval_zscale_maxiterations)
            self.asinh_a.set_value_from_settings(self.scalesModel.stretch_asinh_a)
            self.contrast_contrast.set_value_from_settings(self.scalesModel.stretch_contrastbias_contrast)
            self.contrast_bias.set_value_from_settings(self.scalesModel.stretch_contrastbias_bias)
            self.linear_slope.set_value_from_settings(self.scalesModel.stretch_linear_slope)
            self.linear_intercept.set_value_from_settings(self.scalesModel.stretch_linear_intercept)
            self.log_a.set_value_from_settings(self.scalesModel.stretch_log_a)
            self.powerdist_a.set_value_from_settings(self.scalesModel.stretch_powerdist_a)
            self.power_a.set_value_from_settings(self.scalesModel.stretch_power_a)
            self.sinh_a.set_value_from_settings(self.scalesModel.stretch_sinh_a)
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
        float_none = lambda x: float(x) if x is not None else None
        int_none = lambda x: int(x) if x is not None else None

        settings = QSettings()
        settings.beginGroup("Sliders")

        self.setModelValue('cmap_idx', settings.value("cmap"), model=self.cmapModel)
        self.setModelValue('selected_stretch', settings.value("stretch"))
        self.setModelValue('selected_interval', settings.value("interval"))
        # self.color_combobox.setCurrentIndex(settings.value("cmap", 3))

        self.setModelValue('stretch_asinh_a', float_none(settings.value('asinh/a')))
        self.setModelValue('stretch_contrastbias_contrast', float_none(settings.value('contrast/contrast')))
        self.setModelValue('stretch_contrastbias_bias', float_none(settings.value('contrast/bias')))
        self.setModelValue('stretch_linear_slope', float_none(settings.value('linear/slope')))
        self.setModelValue('stretch_linear_intercept', float_none(settings.value('linear/intercept')))
        self.setModelValue('stretch_log_a', float_none(settings.value('log/a')))
        self.setModelValue('stretch_powerdist_a', float_none(settings.value('powerdist/a')))
        self.setModelValue('stretch_power_a', float_none(settings.value('power/a')))
        self.setModelValue('stretch_sinh_a', float_none(settings.value('sinh/a')))

        self.setModelValue('interval_manual_vmin', float_none(settings.value('manual/vmin')))
        self.setModelValue('interval_manual_vmax', int_none(settings.value('manual/vmax')))
        self.setModelValue('interval_percentile_percentile', float_none(settings.value('percentile/percentile')))
        self.setModelValue('interval_percentile_nsamples', int_none(settings.value('percentile/nsamples')))
        self.setModelValue('interval_asymetric_lower_percentile', float_none(settings.value('asymetric/lpercentile')))
        self.setModelValue('interval_asymetric_upper_percentile', float_none(settings.value('asymetric/upercentile')))
        self.setModelValue('interval_asymetric_nsamples', int_none(settings.value('asymetric/nsamples')))
        self.setModelValue('interval_zscale_nsamples', int_none(settings.value('zscale/nsamples')))
        self.setModelValue('interval_zscale_contrast', float_none(settings.value('zscale/contrast')))
        self.setModelValue('interval_zscale_maxreject', float_none(settings.value('zscale/maxreject')))
        self.setModelValue('interval_zscale_minpixels', int_none(settings.value('zscale/minpixels')))
        self.setModelValue('interval_zscale_krej', float_none(settings.value('zscale/krej')))
        self.setModelValue('interval_zscale_maxiterations', int_none(settings.value('zscale/maxiterations')))
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
