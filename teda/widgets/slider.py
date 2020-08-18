import PySide2
from PySide2.QtCore import Qt, QObject
from PySide2.QtGui import QIntValidator, QDoubleValidator
from PySide2.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout, QLineEdit

class FloatSlider(QWidget):
    """
    Slider with value

    Not used, finished yet
    TODO: Finish and use in place of current sliders
    """

    def __init__(self, #parent=None,
                 f=None, min=None, max=None):
        super().__init__(#parent,
                         f)
        hbox = QHBoxLayout(self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.validator = QDoubleValidator(0.00, 20.00, 2)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        self.slider.setMaximum(20)
        self.line_edit = QLineEdit()
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.line_edit.setValidator(self.validator)
        self.line_edit.setMaxLength(5)

        self.line_edit.setMaximumWidth(50)

        hbox.addWidget(self.slider)
        hbox.addWidget(self.line_edit)

        self.slider.valueChanged.connect(lambda: self.line_edit.setText(str(self.slider.value())))
        self.line_edit.returnPressed.connect(lambda: self.parse_string(self.line_edit.text()))

    def to_slider(self, x:float):
        pass

    def from_slider(self,n:int):
        pass

    def parse_string(self, str):
        str = str.replace(",",".")
        self.slider.setValue(float(str))