from .views.fitsplot import FitsPlotter


class Dragging(FitsPlotter):
    def __init__(self, widget, scale_widget):
        super().__init__()
        self.widget = widget
        self.scale_widget = scale_widget
        self.window_width = widget.centralWidget().width()
        self.window_height = widget.centralWidget().height()
        self.contrast_max_value = 3
        self.contrast_min_value = 0.1
        self.brightness_max_value = 1
        self.brightness_min_value = -1
        self.previous_x = 0
        self.previous_y = 0

    def mouseMoveEvent(self, event):
        contrast = self.calculate_contrast(event.x)
        self.scale_widget.linear_slope.setValue(contrast)
        brightness = self.calculate_brightness(event.y)
        self.scale_widget.linear_intercept.setValue(brightness)

    def calculate_contrast(self, current_x):
        contrast = (current_x/self.window_width)*3
        if self.contrast_max_value >= contrast > self.contrast_min_value:
            return contrast
        elif contrast < self.contrast_min_value:
            return self.contrast_min_value
        else:
            return self.contrast_max_value

    def calculate_brightness(self, current_y):
        brightness = ((current_y/self.window_height)*2)-1
        if self.brightness_max_value >= brightness >= self.brightness_min_value:
            return brightness
        elif brightness < self.brightness_min_value:
            return self.brightness_min_value
        else:
            return self.brightness_max_value
