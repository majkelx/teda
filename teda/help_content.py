"""
Help content for TeDa FITS Viewer
Separated for easy maintenance and updates
"""

HELP_TEXT = """
<div style="text-align: center;">
<a href="https://akond.space"><img src="file://{logo_path}" alt="AkondAstro" style="max-width: 200px; margin: 10px 0;"></a>
<h2>TeDa FITS Viewer - Quick Help</h2>
</div>

<h3>Keyboard Shortcuts</h3>
<p><i>Essential hotkeys for fast workflow:</i></p>
<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; margin-bottom: 15px;">
<tr><th>Key</th><th>Action</th></tr>
<tr><td><b>R</b></td><td>Create radial profile at cursor position (with gaussian fit)</td></tr>
<tr><td><b>H</b></td><td>Create/reposition horizontal line profile at cursor Y</td></tr>
<tr><td><b>V</b></td><td>Create/reposition vertical line profile at cursor X</td></tr>
<tr><td><b>D</b></td><td>Create/reposition diagonal line profile (45° /)</td></tr>
<tr><td><b>Shift+D</b></td><td>Create/reposition diagonal line profile (135° \)</td></tr>
<tr><td><b>Del</b></td><td>Delete selected shape (click shape to select)</td></tr>
<tr><td><b>Ctrl+Drag</b></td><td>Adjust image brightness/contrast dynamically</td></tr>
<tr><td><b>Ctrl+O</b></td><td>Open FITS file</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save image view</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Quit application</td></tr>
</table>

<h3>Opening Files</h3>
<ul>
<li><b>File → Open</b> or <b>Ctrl+O</b>: Open a FITS file</li>
<li><b>File Browser</b> (left panel): Browse and double-click files</li>
<li><b>Right-click file</b>: Copy file path to clipboard</li>
<li><b>Command line</b>: <code>teda myfile.fits</code> or <code>teda /path/to/directory</code></li>
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
<li><b>Radial Profile</b> (R key): Click to create centered circle with gaussian fit
  <ul>
  <li>Shows FWHM, RMS, and sky level on chart</li>
  <li>Status bar displays area statistics (mean, std, range) for all encircled pixels</li>
  </ul>
</li>
<li><b>Linear Profile</b> (H/V/D keys): Analyze intensity along a line
  <ul>
  <li>H: Horizontal line at cursor Y</li>
  <li>V: Vertical line at cursor X</li>
  <li>D: Diagonal line (45° /), Shift+D: (135° \)</li>
  <li>Or use the timeline toolbar button and draw custom line</li>
  <li>Status bar displays profile statistics (mean, std, range)</li>
  </ul>
</li>
<li><b>Info panel</b>: Displays filename, pixel value, coordinates, WCS in real-time</li>
<li><b>Status bar</b>: Shows statistics for Linear profile, Radial profile area, and whole Image</li>
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

<h3>Configuration & CLI Options</h3>
<ul>
<li><b>View → Reset Layout</b>: Reset window layout to defaults</li>
<li><b>teda /path/to/file.fits</b>: Open specific FITS file on startup</li>
<li><b>teda /path/to/directory</b>: Set file explorer to specific directory on startup</li>
<li><b>teda --reset-config</b>: Reset all settings (layout, sliders, pins, last file)</li>
<li><b>teda --reset-layout</b>: Reset only window layout and dock positions</li>
<li><b>teda --ignore-settings</b> or <b>-i</b>: Start without loading saved configuration</li>
<li><b>teda --help</b>: Show all command-line options</li>
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
<div style="text-align: center;">
<p><i>For detailed documentation, bug reports, and updates, visit:<br>
<a href="https://github.com/majkelx/teda">github.com/majkelx/teda</a></i></p>
<p style="margin-top: 15px;"><a href="https://akond.space"><img src="file://{logo_path}" alt="AkondAstro" style="max-width: 150px;"></a><br>
<i>Created by <a href="https://akond.space">AkondAstro</a> with cooperation of the OCM observatory</i></p>
</div>
"""
