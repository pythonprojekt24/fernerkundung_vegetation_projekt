# einfügen von Geländemodell durch die google earth engine, funktioniert noch nicht aber hoffentlich bald

import ee
import geemap
import webbrowser

# Authenticate and initialize the Earth Engine module.
ee.Authenticate()
ee.Initialize()

# Load the SRTM dataset.
dataset = ee.Image('CGIAR/SRTM90_V4')

# Select the elevation band.
elevation = dataset.select('elevation')

# Calculate the slope.
slope = ee.Terrain.slope(elevation)

# Create an interactive map.
m = geemap.Map()
m.set_center(-112.8598, 36.2841, 10)
m.add_layer(slope, {'min': 0, 'max': 60}, 'slope')

# Save the map to an HTML file.
map_file = 'plots\slope_map.html'
m.save(map_file)

# Open the map in the default web browser.
webbrowser.open(map_file)


