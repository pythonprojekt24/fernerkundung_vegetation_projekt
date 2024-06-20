import ee
import geemap
import webbrowser
import os

# Replace 'your-project-id' with your actual project ID
project_id = 'ee-mascherjo'

# Authenticate and initialize the Earth Engine module with the project ID.
ee.Authenticate()
ee.Initialize(project=project_id)

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
map_file = os.path.join('plots', 'slope_map.html')
if not os.path.exists('plots'):
    os.makedirs('plots')
m.save(map_file)

# Open the map in the default web browser.
webbrowser.open('file://' + os.path.realpath(map_file))
