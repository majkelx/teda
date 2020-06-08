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
``` 
To use ipython console, additionally:
``` bash
    pip install qtconsole
``` 

## Development version install:
``` bash

    git clone git@github.com:majkelx/teda.git
    cd teda
    python -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
```
