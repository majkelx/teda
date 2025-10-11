"""
Help content for TeDa FITS Viewer
Separated for easy maintenance and updates
"""

HELP_TEXT = """
<h2>TeDa FITS Viewer - Quick Help</h2>

<h3>Opening Files</h3>
<ul>
<li><b>File → Open</b> or <b>Ctrl+O</b>: Open a FITS file</li>
<li><b>File Browser</b> (left panel): Browse and double-click files</li>
<li><b>Right-click file</b>: Copy file path to clipboard</li>
<li><b>Command line</b>: <code>teda myfile.fits</code></li>
</ul>

<h3>Navigation & Zoom</h3>
<ul>
<li><b>Zoom toolbar</b>: ×4, ×2, Home, ½, ¼ buttons</li>
<li><b>Panning mode</b> (default): Click and drag to pan the image</li>
<li><b>Zoom view</b>: Shows magnified region around cursor</li>
<li><b>Full view</b>: Shows entire image with viewport rectangle</li>
</ul>

<h3>Image Analysis</h3>
<ul>
<li><b>R key</b>: Create radial profile at cursor position</li>
<li><b>Radial Profile Fit</b>: Shows FWHM and gaussian fit parameters</li>
<li><b>Info panel</b>: Displays filename, pixel value, coordinates, WCS</li>
<li><b>Auto Center</b> (Edit menu): Automatically center on star centroid</li>
</ul>

<h3>Dynamic Scale</h3>
<ul>
<li><b>Stretch</b>: asinh, linear, log, sqrt, square, etc.</li>
<li><b>Interval</b>: zscale, percentile, min/max, histogram</li>
<li><b>Ctrl+Drag</b>: Adjust brightness/contrast with mouse</li>
<li><b>View → Dynamic Scale Sliders</b>: Show/hide scale controls</li>
</ul>

<h3>Regions & Shapes</h3>
<ul>
<li><b>Circle tool</b>: Click to add circular regions</li>
<li><b>Radial profile tool</b>: Click to add centered circle with fit</li>
<li><b>Delete key</b>: Delete selected shape (click to select)</li>
<li>Shapes sync across main, zoom, and full views</li>
</ul>

<h3>Multi-HDU Files</h3>
<ul>
<li><b>HDU menu</b>: Navigate between HDU extensions</li>
<li><b>Prev/Next HDU</b>: Toolbar buttons for quick navigation</li>
<li><b>FITS header panel</b>: View and pin important header keywords</li>
</ul>

<h3>Directory Scanning</h3>
<ul>
<li><b>File → Scan</b>: Monitor directory for new FITS files</li>
<li><b>Auto-pause</b>: Pauses scan on mouse movement, resumes after 5s idle</li>
<li>Useful for real-time observatory data acquisition</li>
</ul>

<h3>WCS Coordinates</h3>
<ul>
<li><b>WCS → Sexagesimal</b>: Toggle RA/Dec format (HH:MM:SS vs degrees)</li>
<li><b>WCS → Show Grid</b>: Overlay coordinate grid on image</li>
<li>WCS info updates in real-time as cursor moves</li>
</ul>

<h3>Configuration</h3>
<ul>
<li><b>View → Reset Layout</b>: Reset window layout to defaults</li>
<li><b>--reset-config</b>: Command-line option to reset all settings</li>
<li><b>--ignore-settings</b>: Start without loading saved configuration</li>
<li>Settings saved automatically on exit</li>
</ul>

<h3>Advanced Features</h3>
<ul>
<li><b>Python Console</b> (View menu): Interactive IPython console with access to data, header, wcs, axes</li>
<li><b>Save Image</b> (Ctrl+S): Export view as PNG, PDF, SVG, etc.</li>
<li>All dock panels can be rearranged, floated, or hidden</li>
</ul>

<h3>Tips</h3>
<ul>
<li>Hover over toolbar buttons for tooltips</li>
<li>Info panel fields are read-only but allow text selection and copying</li>
<li>Dynamic Scale window cannot be docked (always floating)</li>
<li>Use <code>teda --help</code> for command-line options</li>
</ul>

<hr>
<p><i>For detailed documentation, bug reports, and updates, visit:<br>
<a href="https://github.com/majkelx/teda">github.com/majkelx/teda</a></i></p>
"""
