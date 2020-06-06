import os
from PySide2.QtGui import QIcon


class IconFactory(object):
    icons_dir = os.path.join(os.path.split(__file__)[0], 'icons')
    icon_formats = ['svg', 'png']

    @classmethod
    def getIcon(cls, name):
        for ext in cls.icon_formats:
            path = os.path.join(cls.icons_dir, name+'.'+ext)
            if os.path.isfile(path):
                return QIcon(path)
        return QIcon()
