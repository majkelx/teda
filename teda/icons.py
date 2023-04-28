import os
from PySide6.QtGui import QIcon


class IconFactory(object):
    # subdir = 'icons'
    subdir = 'icons'
    prefix = ''
    suffix = '-24px'
    icon_formats = ['svg', 'png']


    icons_dir = os.path.join(os.path.split(__file__)[0], subdir)

    @classmethod
    def getIcon(cls, name=None):
        if name is None:
            return QIcon()
        for ext in cls.icon_formats:
            path = os.path.join(cls.icons_dir, cls.prefix+name+cls.suffix+'.'+ext)
            if os.path.isfile(path):
                return QIcon(path)
        return QIcon()
