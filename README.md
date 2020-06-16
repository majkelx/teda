# TeDa FITS Viewer

Observatory optimized SAO DS9 replacement

## Key Features
* Flexible windows and widgets layout
* WCS support
* Radial Profile with gaussoide fit (try `r`-key)
* Scan mode: observes directory for changes and automatically opens new FITS
* Integrated ipython console with direct access to data and application

## Installation
``` bash
   pip install teda
   teda_viewer 
``` 
To use ipython console, additionally:
``` bash
    pip install qtconsole
``` 

## Run
The installation scripts should install the command:
```
    teda_viewer
```
Try 
```
    teda_viewer --help
```
for list of command line parameters.

## Fits Header Cards Pinning
On the FITS Header panel, selected keys can be *pinned* to appear
on the top ot the list. This can be done via context (right-click) menu.

The set of pinned keys is saved and preserved between sessions.  

## Integrated Python Console
In order to use integrated python console the `qtconsole` module, and it's
dependencies (jupyter related) have to be installed. This is not done by
default `pip` installation to keep number of dependencies reasonably small.
Install `qtconsole` by:
``` bash
    pip install qtconsole
``` 
### Predefined variables
The console has a number of predefined variables set:

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

After pressing **Scan** button, and choosing directory, TeDa Fits Viewer will
load most recent FITS file from that directory, and keep watching the directory 
for changes. When new FITS file is added to directory, it will be loaded 
automatically.

To avoid loading new files when inspecting current one, pause scanning by **Pause**
button.

This mode is intended to observe newly created FITS files in observatory. 

## Development version install
``` bash

    git clone git@github.com:majkelx/teda.git
    cd teda
    python -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
```

## Bugs, remarks, greetings and contribution 
Please use [GitHub issues tracker](https://github.com/majkelx/teda/issues) 
and [pull requests](https://github.com/majkelx/teda/pulls).


@2020  [AkondLab](http://www.akond.com) for the [Araucaria Project](https://araucaria.camk.edu.pl).