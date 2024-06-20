import ee

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

# Define the region of interest (ROI) using approximate WGS84 coordinates
min_lon, min_lat = 6.21, 51.28
max_lon, max_lat = 7.26, 54.16
roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])

# Set export parameters
export_task = ee.batch.Export.image.toDrive(
    image=elevation,
    description='Europe_Slope',
    folder='EarthEngineImages',
    fileNamePrefix='elevation_smalleurope',
    region=roi,
    scale=1000,  # Adjust the scale as needed
    crs='EPSG:4326',
    maxPixels=1e13
)

# Start the export task
export_task.start()

print("Exporting GeoTIFF... Check the GEE tasks in your GEE Console to monitor the export process.")
