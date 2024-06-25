import geopandas as gpd
from shapely.geometry import Polygon


# Define the coordinates for Munich and Mantova
munich_lat = 48.1351
munich_lon = 11.5820
mantova_lat = 45.1562
mantova_lon = 10.7925

# Calculate the center point
center_lat = (munich_lat + mantova_lat) / 2
center_lon = (munich_lon + mantova_lon) / 2

# Calculate the distance in degrees
lat_diff = abs(munich_lat - mantova_lat)
lon_diff = abs(munich_lon - mantova_lon)

# Define a buffer to ensure the cities are within the square and avoid the sea
buffer = 0.5

# Determine the side length of the square (in degrees)
side_length = max(lat_diff, lon_diff) + buffer

# Calculate the bounding box coordinates
min_lat = center_lat - side_length / 2
max_lat = center_lat + side_length / 2
min_lon = center_lon - side_length / 2
max_lon = center_lon + side_length / 2

# Ensure the bounding box is within mainland boundaries (approximate)
if min_lat < 44.0: min_lat = 44.0
if max_lat > 49.0: max_lat = 49.0
if min_lon < 5.0: min_lon = 5.0
if max_lon > 15.0: max_lon = 15.0

# Create a square bounding box in WGS84 coordinates
bbox_wgs84 = Polygon([(min_lon, min_lat), (max_lon, min_lat), (max_lon, max_lat), (min_lon, max_lat), (min_lon, min_lat)])

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame([{'geometry': bbox_wgs84}], crs='EPSG:4326')

# Save the GeoDataFrame to a shapefile
gdf.to_file('munich_mantova_square_centered2.shp')

print("Shapefile created successfully!")


