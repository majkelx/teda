from setuptools import setup
import teda.version

# SEE: https://packaging.python.org/tutorials/packaging-projects/ for clues of changes

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='teda',
    version=teda.version.__version__,
    packages=['teda', 'teda.views', 'teda.models', 'teda.widgets', 'teda.painterShapes'],
    url='https://github.com/majkelx/teda',
    license='MIT',
    author='Akond Lab',
    author_email='',
    description='TeDa FITS Viewer',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={'teda': ['icons/*']},
    entry_points={
        # "console_scripts": [
        #     "teda_viewer = teda_fits:main",
        # ],
        "gui_scripts": [
            "teda_viewer = teda.teda_fits:main",
        ]
    },
    install_requires=[
        'pyside2',
        'astropy',
        'matplotlib',
        'scipy',
        'traitlets',
#        'watchdog',
    ],
)
