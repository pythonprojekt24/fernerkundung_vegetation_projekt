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

# Define the region of interest (ROI) for Europe.
europe_roi = ee.Geometry.Polygon([
    [[-31.266, 34.5], [44.561, 34.5], [44.561, 71.2], [-31.266, 71.2], [-31.266, 34.5]]
])

# Set export parameters
export_task = ee.batch.Export.image.toDrive(
    image=elevation,
    description='Europe_Slope',
    folder='EarthEngineImages',
    fileNamePrefix='elevation_europe',
    region=europe_roi,
    scale=1000,  # Adjust the scale as needed
    crs='EPSG:4326',
    maxPixels=1e13
)

# Start the export task
export_task.start()

print("Exporting GeoTIFF... Check the GEE tasks in your GEE Console to monitor the export process.")
