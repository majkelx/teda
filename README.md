# ![TeDa](img/teda_logo.png) TeDa FITS Viewer

Observatory optimized FITS Images viewer


[![PyPI](https://img.shields.io/pypi/v/teda.svg)](https://pypi.org/project/teda/)
[![Python Version](https://img.shields.io/pypi/pyversions/teda.svg)](https://pypi.org/project/teda/)
[![License](https://img.shields.io/pypi/l/teda.svg)](https://pypi.org/project/teda/)
[![Downloads](https://pepy.tech/badge/teda)](https://pepy.tech/project/teda)


![TeDa Screenshot](img/teda.png)

## Key Features
* Flexible windows and widgets layout
* WCS support
* **Radial Profile** with gaussian fit - press `R` key at cursor position
  * Displays FWHM, RMS, and sky level
  * Shows area statistics (mean, std, range) in status bar
* **Linear Profile** - keyboard shortcuts for quick positioning:
  * `H` - horizontal line at cursor Y
  * `V` - vertical line at cursor X
  * `D` - diagonal line (45°), `Shift+D` - diagonal (135°)
  * Free hand line drawing with mouse
  * Shows profile statistics in status bar
* **Real-time Statistics** in status bar for Linear profile, Radial area, and whole Image
* Integrated file browser with directory tree and files list for quick navigation and opening
* Pinnable FITS header cards
* Scan mode: observes directory for changes and automatically opens new FITS
* Integrated ipython console with direct access to data and application
* **Quick Help** with keyboard shortcuts reference (press `?` button or F1)

## Installation
The safest and recommended way to install TeDa is to use `pipx`:
``` bash
pipx install teda
```

### Linux Desktop Integration
After installation on Linux, you can add TeDa to your application menu:
```bash
teda --install-desktop
```

This will:
* Install the application icon and desktop entry
* Make TeDa appear in your application menu
* Add TeDa to favorites panel (on GNOME/Ubuntu)

To remove the desktop entry:
```bash
teda --uninstall-desktop
```

Consult [pipx documentation](https://pipxproject.github.io/pipx/) for pipx installation instructions.

### Optional dependencies
To use ipython console the `console` extra should be specified.
This extra installs `ipython` and `qtconsole` packages.
``` bash
    pipx install teda[console]
```

For directory scanning functionality, the `watchdog` package should be installed, e.g. 
``` bash
    pipx install teda[watchdog]
``` 

## Run
After installation, run TeDa from terminal:
```bash
teda
```

If the command is not found, ensure pipx binaries are in your PATH:
```bash
pipx ensurepath
```

On Linux, after running `teda --install-desktop`, you can also launch TeDa from your application menu. 

## Command line parameters

Open specific FITS file:
```bash
    teda /path/to/file.fits
```

Open with file explorer set to specific directory:
```bash
    teda /path/to/directory
```

View all command line options:
```bash
    teda --help
```

Useful options:
* `--reset-layout` - Reset window layout to defaults
* `--reset-config` - Reset all configuration (layout, sliders, pins, last file)
* `-i` or `--ignore-settings` - Start without loading saved configuration

## Dynamic Scale and Color
The dynamic scale of the image, and color mapping can be adjusted form 
the **Dynamic Scale** panel. From menu: **View/Dynamic Scale**

## Fits Header Cards Pinning
On the FITS Header panel, selected keys can be *pinned* to appear
on the top ot the list. This can be done via context (right-click) menu.

The set of pinned keys is saved and preserved between sessions.  

## Keyboard Shortcuts

TeDa provides convenient keyboard shortcuts for fast workflow:

* `R` - Create radial profile at cursor position (with gaussian fit)
* `H` - Horizontal line profile at cursor Y
* `V` - Vertical line profile at cursor X
* `D` - Diagonal line profile (45° /)
* `Shift+D` - Diagonal line profile (135° \)
* `Del` - Delete selected shape
* `Ctrl+Drag` - Adjust image brightness/contrast dynamically
* `Ctrl+O` - Open FITS file
* `Ctrl+S` - Save image view
* `F1` - Show quick help with all shortcuts

Press the `?` button in the toolbar for complete keyboard shortcuts reference.

## Radial Profile
The **Radial Profile** button turns on the mode of selecting targets for
the radial profile analysis. Make sure the radial profile panel is visible
(View/Radial Profile). The shortcut for displaying radial profile of the star
under cursor is the **R** key.

The centroid of the star is corrected within small (be precise!) radius
using the bivariate gaussian fit.

Together with the pixel values, the radial profile presents 1D fit of
"gaussian(r) + sky". This fit provides FWHM and sky level information on the chart.

**Status bar** displays area statistics (mean, median, std, min, max) for all pixels
within the encircled area, calculated in background for performance.

## Linear Profile
The **Linear Profile** tool (timeline icon in toolbar) allows analyzing intensity
along a line. Quick keyboard shortcuts:

* `H` - Horizontal line at cursor Y position (full width)
* `V` - Vertical line at cursor X position (full height)
* `D` - Diagonal line at 45° (/) passing through cursor
* `Shift+D` - Diagonal line at 135° (\) passing through cursor

Or use the toolbar button to draw custom lines interactively.

The **Linear Profile** panel displays the intensity plot, and the **status bar**
shows profile statistics (mean, std, value range) for all pixels along the line.
   

## Integrated Python Console
In order to use integrated python console the `console` extra dependency group have to be installed

The console is available form menu **View/Python Console**

### Predefined variables
The console has a number of predefined variables set:
* `ax: WCSAxesSubplot` main plotting axes.
* `window: MainWindow` main window
* `data: numpy.ndarray` current HDU data
* `header: astropy.fits.Header` current HDU header
* `wcs: astropy.wcs.WCS` the WCS transformer

### Plotting
To plot directly on the console, run the following magic command `%matplotlib inline`.

When plotting on the main canvas, the result will appear after redrawing
main figure by `ax.figure.canvas.draw()`.

The example below, draws linear profile on the console and corresponding
line on the main FITS display:    
  
``` python
%matplotlib inline
import matplotlib.pyplot as plt
ax.plot([10,30], [10,10])
ax.figure.canvas.draw()
plt.plot(data[10,10:30])
```

## Directory Scan
The **Scan Toolbar** (hidden by default) provides controls for the 
directory scanning mode.

This mode is intended to observe newly created FITS files in observatory.

After pressing **Scan** button, and choosing directory, TeDa Fits Viewer will
load most recent FITS file from that directory, and keep watching the directory 
for changes. When new FITS file is added to directory, it will be loaded 
automatically.

User can pause scanning using **Pause** button. There is also **auto pause** feature,
when active, any mouse movement in the main area pauses scanning for 5 seconds,
avoiding FITS reload when working.

After un-pausing (manually or after idle 5 seconds when auto-pause) the newest
FITS will be loaded if any new files appeared during the pause.

Directory scanning needs the `watchdog` extra dependency to be 
installed (see Installation above).

## Directory Panel
The Directory Panel can be shown using menu command **View-Directory view**.

The Directory Panel is convenient files navigator. The panel has two views:
* Directory Tree
* Files List

User can collapse any of them using divider handle and use only remaining one.
If the tree view is the only visible, it shows directories and files as well.      

## Development version install
TeDa uses [poetry](https://python-poetry.org/) for development and packaging.

``` bash

    git clone https://github.com/majkelx/teda.git
    cd teda
    poetry install
```

## Bugs, remarks, greetings and contribution 
Please use [GitHub issues tracker](https://github.com/majkelx/teda/issues) 
and [pull requests](https://github.com/majkelx/teda/pulls).


@2020-2025  [AkondAstro](https://akond.space) for the [Araucaria Project](https://araucaria.camk.edu.pl).
