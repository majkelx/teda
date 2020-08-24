import PySide2
from PySide2.QtGui import QDoubleValidator, QIntValidator, QValidator
from PySide2.QtCore import Qt, Signal, Slot, QLocale
from PySide2.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout, QLineEdit

class FloatSlider(QWidget):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """
    slider_min = 0
    slider_max = 20
    slider_step = 10
    edit_line_width = 45

    valueChanged = Signal(float)

    def __init__(self, #parent = None,
                 min=0,
                 max=100):
        # super().__init__(parent)
        super().__init__()
        self.min = min
        self.max = max
        self.locale = QLocale(QLocale.German, QLocale.Germany)
        self.validator = QDoubleValidator()
        hbox = QHBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(self.slider_min)
        self.slider.setMaximum(self.slider_max)
        self.slider.setSingleStep(self.slider_step)
        self.line_edit = QLineEdit('', self)
        self.line_edit.setValidator(self.validator)
        self.line_edit.setMaximumWidth(self.edit_line_width)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.line_edit)

        self.slider.valueChanged.connect(lambda: self._on_slider_moved(self.slider.value()))
        self.line_edit.editingFinished.connect(lambda: self._on_edit_finished(self.line_edit.text()))

    @Slot(int)
    def setValue(self, val: int): # float
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
        normalized_value = self._from_slider(val)
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


class IntSlider(QWidget):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """
    slider_min = 0
    slider_max = 20
    slider_step = 1
    edit_line_width = 45
    valueChanged = Signal(int)

    def __init__(self, #parent=None,
                 min=0,
                 max=100):
        #super().__init__(parent)
        super().__init__()
        self.locale = QLocale(QLocale.German, QLocale.Germany)
        self.validator = QIntValidator()
        self.max = max
        self.min = min
        hbox = QHBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(self.slider_min)
        self.slider.setMaximum(self.slider_max)
        self.slider.setSingleStep(self.slider_step)
        self.edit_line = QLineEdit('', self)
        self.edit_line.setMaximumWidth(self.edit_line_width)
        self.edit_line.setValidator(self.validator)

        hbox.addWidget(self.slider)
        hbox.addWidget(self.edit_line)

        self.slider.valueChanged.connect(lambda: self._on_slider_moved(self.slider.value()))

        self.edit_line.editingFinished.connect(lambda: self._on_edit_finished(self.edit_line.text()))

    @Slot(int)
    def setValue(self, val: int): # float
        str_value = self.locale.toString(val)
        normalized_value = self._to_slider(val)
        self.edit_line.setText(str_value)
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
        self.edit_line.setText(str_value)
        self.valueChanged.emit(normalized_value)

    def _to_slider(self, val: int):  # float
        normalized = 1.0 * (val - self.min) / (self.max - self.min)
        slider = normalized * self.slider_max
        return slider

    def _from_slider(self, slider_val: int):  # int
        normalized = 1.0 * slider_val / self.slider_max
        if self.min != 0:
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