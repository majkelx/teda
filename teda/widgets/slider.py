import PySide2
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout

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
