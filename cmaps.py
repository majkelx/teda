from collections import OrderedDict
from traitlets import HasTraits, Int, Unicode
import matplotlib.colors
import matplotlib.pyplot as plt

class ColorMaps(HasTraits):
    default = 'bone'
    cmap_idx = Unicode(default_value=default)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.colormaps = OrderedDict()

        self.colormaps['greens'] = matplotlib.colors.LinearSegmentedColormap.from_list('zielonka', ['g', 'w'], )
        self.colormaps['gray'] = plt.get_cmap('gist_gray')
        self.colormaps['heat'] = plt.get_cmap('gist_heat')
        self.colormaps['bone'] = plt.get_cmap('bone')
        self.colormaps['cmr'] = plt.get_cmap('CMRmap')

        for c, map in list(self.colormaps.items()):
            self.colormaps[c + ' inv'] = map.reversed()

    def set_active_color_map(self, mapname):
        """ map as int index or string"""
        self.cmap_idx = mapname

    def get_active_color_map(self):
        return self.colormaps[self.cmap_idx]



