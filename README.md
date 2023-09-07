# TeDa FITS Viewer

Observatory optimized FITS Images viewer

![](img/teda.png)

## Key Features
* Flexible windows and widgets layout
* WCS support
* Radial Profile with gaussoide fit (try `r`-key)
* Scan mode: observes directory for changes and automatically opens new FITS
* Integrated ipython console with direct access to data and application

## Installation
The safest and recommended way to install TeDa is to use `pipx`:
``` bash
   pipx install teda
   teda 
``` 
Consult [pipx documentation](https://pipxproject.github.io/pipx/) for installation instructions.

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
The installation scripts should install the command:
```
    teda
```
if it is not working, try:
```
    pipx ensurepath 
```
to add pipx-installed binaries to your path. 

## Command line parameters
```
    teda --help
```
for list of command line parameters.

## Dynamic Scale and Color
The dynamic scale of the image, and color mapping can be adjusted form 
the **Dynamic Scale** panel. From menu: **View/Dynamic Scale**

## Fits Header Cards Pinning
On the FITS Header panel, selected keys can be *pinned* to appear
on the top ot the list. This can be done via context (right-click) menu.

The set of pinned keys is saved and preserved between sessions.  

## Radial Profile
The **Radial Profile** button turns on the mode of selecting targets for 
the radial profile analysis. Make sure the radial profile panel is visible 
(View/Radial Profile). The shortcut for displaying radial profile of the star 
under cursor is the **R**-key.

The centroid of the star is corrected within small (be precise!) radius
using the bivariate gaussoide fit.

Together with the pixels values, the radial profile presents 1D fit of
"gaussian(r) + sky". This fit provides information of presented fwhm and sky level.
   

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


@2020-2023  [AkondLab](http://www.akond.com) for the [Araucaria Project](https://araucaria.camk.edu.pl).
