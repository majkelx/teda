import PySide2
from PySide2.QtCore import Qt, Signal, Slot, QLocale
from PySide2.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout, QLineEdit


class FloatSlider(QWidget):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """

    def __init__(self, parent = None,
                 f = None):
        super().__init__(parent, f)
        hbox = QHBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.label = QLabel('', self)

        hbox.addWidget(self.slider)
        hbox.addWidget(self.label)

        self.slider.valueChanged.connect()
        self.label.connect(self.slider, )


class IntSlider(QWidget):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """

    slidermax = 20

    valueChanged = Signal(int)

    def __init__(self, parent=None, nim=0, max=100):
        super().__init__(parent)

        hbox = QHBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.label = QLineEdit('', self)

        hbox.addWidget(self.slider)
        hbox.addWidget(self.label)

        self.slider.sliderMoved.connect(self._on_slider_moved)
        # self.label.connect(self.slider, )

        self.label.editingFinished.connect(self._on_edit_finished)


    @Slot(int)
    def setValue(self, val: int): # float
        vstr = QLocale.toStr(val)
        slider = self._to_slider(val)
        self.label.setText(vstr)
        self.slider.setValue(slider)


    @Slot(str)
    def _on_edit_finished(self, valstr):
        v = QLocale.toInt(valstr)
        self.slider.setValue(self._to_slider(v))
        self.valueChanged.emit(v)

    @Slot(int)
    def _on_slider_moved(self, val):
        v = self._from_slider(val)
        vstr = QLocale.toStr(val)
        self.label.setText(vstr)
        self.valueChanged.emit(v)

    def _to_slider(self, val: int):  # float
        normalized = 1.0 * (val - self.min) / (self.max - self.min)
        slider = normalized * self.slidermax
        return slider

    def _from_slider(self, slider_val: int):  # int
        normalized = 1.0 * slider_val / self.slidermax
        val = normalized * (self.max - self.min) - self.min
        return val

