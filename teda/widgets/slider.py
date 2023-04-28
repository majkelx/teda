import PySide6
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt, Signal, Slot, QLocale
from PySide6.QtWidgets import QWidget, QSlider, QHBoxLayout, QLineEdit, QSizePolicy


class LabeledSlider(QWidget):
    slider_min = 0
    slider_max = 64
    slider_step = 1
    line_edit_width = 70
    line_edit_heigth = 20

    def __init__(self):
        super().__init__()
        self.locale = QLocale()
        self.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0,)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(self.slider_min)
        self.slider.setMaximum(self.slider_max)
        self.slider.setSingleStep(self.slider_step)
        self.line_edit = QLineEdit('', self)
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.line_edit.setMaximumWidth(self.line_edit_width)
        self.line_edit.setMaximumHeight(self.line_edit_heigth)
        self.line_edit.setMinimumHeight(self.line_edit_heigth)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.line_edit)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)


class FloatSlider(LabeledSlider):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """

    valueChanged = Signal(float)

    def __init__(self, #parent = None,
                 min=0,
                 max=100):
        # super().__init__(parent)
        super().__init__()
        self.validator = QDoubleValidator()
        self.min = min
        self.max = max
        self.line_edit.setValidator(self.validator)

        self.slider.valueChanged.connect(lambda: self._on_slider_moved(self.slider.value()))
        self.line_edit.editingFinished.connect(lambda: self._on_edit_finished(self.line_edit.text()))

    @Slot(int)
    def setValue(self, val):
        str_value = self.locale.toString(val)
        normalized_value = self._to_slider(val)
        self.line_edit.setText(str_value)
        self.slider.setValue(normalized_value)

    @Slot(str)
    def _on_edit_finished(self, valstr):
        f_value = self.locale.toFloat(valstr)[0]
        validated_value = self.validate_input(f_value)
        normalized_value = self._to_slider(validated_value)
        self.slider.setValue(normalized_value)
        self.valueChanged.emit(validated_value)

    @Slot(int)
    def _on_slider_moved(self, val):
        value = self._from_slider(val)
        normalized_value = self.normalize_to_two_decimals_value(value)
        str_value = self.locale.toString(normalized_value)
        self.line_edit.setText(str_value)
        self.valueChanged.emit(normalized_value)

    def _to_slider(self, val: float):  # float
        normalized = 1.0 * (val - self.min) / (self.max - self.min)
        slider = normalized * self.slider_max
        return slider

    def _from_slider(self, slider_val: int):  # int
        normalized = 1.0 * slider_val / self.slider_max
        if self.min != 0.0:
            val = normalized * (self.max - self.min) + self.min
        else:
            val = normalized * (self.max - self.min) - self.min
        return val

    def get_value(self):
        return self.slider.value()

    def validate_input(self, input_value):
        if input_value > self.max:
            return self.max
        elif input_value < self.min:
            return self.min
        else:
            return input_value

    def set_value_from_settings(self, value):
        val = self.validate_input(value)
        self.setValue(val)

    def normalize_to_two_decimals_value(self, value):
        return float("{:.2f}".format(value))


class IntSlider(LabeledSlider):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """
    valueChanged = Signal(int)

    def __init__(self, #parent=None,
                 min=0,
                 max=100):
        #super().__init__(parent)
        super().__init__()
        self.validator = QIntValidator()
        self.max = max
        self.min = min
        self.line_edit.setValidator(self.validator)
        self.slider.setMinimum(self.min)
        self.slider.setMaximum(self.max)
        self.slider.setSingleStep((self.max - self.min)//100 + 1)

        self.slider.valueChanged.connect(lambda: self._on_slider_moved(self.slider.value()))
        self.line_edit.editingFinished.connect(lambda: self._on_edit_finished(self.line_edit.text()))

    @Slot(int)
    def setValue(self, val):
        str_value = self.locale.toString(val)
        normalized_value = self._to_slider(val)
        self.line_edit.setText(str_value)
        self.slider.setValue(normalized_value)

    @Slot(str)
    def _on_edit_finished(self, valstr):
        i_value = self.locale.toInt(valstr)[0]
        validated_value = self.validate_input(i_value)
        self.slider.setValue(self._to_slider(validated_value))
        self.valueChanged.emit(validated_value)

    @Slot(int)
    def _on_slider_moved(self, val):
        normalized_value = self._from_slider(val)
        str_value = self.locale.toString(normalized_value)
        self.line_edit.setText(str_value)
        self.valueChanged.emit(normalized_value)

    def _to_slider(self, val: int):  # float
        return val
        # normalized = 1.0 * (val - self.min) / (self.max - self.min)
        # slider = normalized * self.slider_max
        # return slider

    def _from_slider(self, slider_val: int):  # int
        return slider_val
        # normalized = 1.0 * slider_val / self.slider_max
        # if self.min != 0:
        #     val = normalized * (self.max - self.min) + self.min
        # else:
        #     val = normalized * (self.max - self.min) - self.min
        # return val

    def get_value(self):
        return self.slider.value()

    def validate_input(self, input_value):
        if input_value > self.max:
            return self.max
        elif input_value < self.min:
            return self.min
        else:
            return input_value

    def set_value_from_settings(self, value):
        val = self.validate_input(value)
        self.setValue(val)