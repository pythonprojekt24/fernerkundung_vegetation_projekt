import geopandas as gpd
from shapely.geometry import Point, Polygon
import pyproj

################################# shapefile rund um IBK #########################
# # Define the center point (latitude and longitude) for Innsbruck
# center_lat = 47.2689
# center_lon = 11.3929

# # Define the buffer radius in meters (100 km)
# buffer_radius = 100000  # 100 km

# # Create a point geometry for the center
# center_point = Point(center_lon, center_lat)

# # Define the projection (WGS84 to UTM for accurate distance buffering)
# wgs84 = pyproj.CRS('EPSG:4326')  # WGS84 coordinate system
# utm = pyproj.CRS('EPSG:32632')  # UTM zone for Innsbruck

# # Project the center point to UTM
# project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
# center_point_utm = center_point
# center_point_utm = Point(*project(center_point_utm.x, center_point_utm.y))

# # Create a buffer around the center point in UTM coordinates
# buffer_utm = center_point_utm.buffer(buffer_radius)

# # Project the buffer back to WGS84
# inverse_project = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True).transform
# buffer_wgs84 = Polygon([inverse_project(*coord) for coord in buffer_utm.exterior.coords])

# # Create a GeoDataFrame
# gdf = gpd.GeoDataFrame([{'geometry': buffer_wgs84}], crs='EPSG:4326')

# # Save the GeoDataFrame to a shapefile
# gdf.to_file('innsbruck_buffer_100km.shp')

# print("Shapefile created successfully!")

################################################# Shapefile München - Mantova ######################################################
# # Define the coordinates for Munich and Mantova
# munich_lat = 48.1351
# munich_lon = 11.5820
# mantova_lat = 45.1562
# mantova_lon = 10.7925

# # Define the projection (WGS84)
# wgs84 = pyproj.CRS('EPSG:4326')

# # Create points for Munich and Mantova
# munich_point = (munich_lon, munich_lat)
# mantova_point = (mantova_lon, mantova_lat)

# # Define the UTM zone that covers both points
# utm_zone = 32
# utm = pyproj.CRS(f'EPSG:326{utm_zone}')

# # Project points to UTM for accurate distance measurements
# project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
# munich_point_utm = project(munich_lon, munich_lat)
# mantova_point_utm = project(mantova_lon, mantova_lat)

# # Calculate the bounding box in UTM coordinates
# min_x = min(munich_point_utm[0], mantova_point_utm[0])
# max_x = max(munich_point_utm[0], mantova_point_utm[0])
# min_y = min(munich_point_utm[1], mantova_point_utm[1])
# max_y = max(munich_point_utm[1], mantova_point_utm[1])

# # Ensure the bounding box is square by adjusting the sides
# side_length = max(max_x - min_x, max_y - min_y)
# max_x = min_x + side_length
# max_y = min_y + side_length

# # Create a square bounding box in UTM coordinates
# bbox_utm = Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y), (min_x, min_y)])

# # Project the bounding box back to WGS84
# inverse_project = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True).transform
# bbox_wgs84 = Polygon([inverse_project(*coord) for coord in bbox_utm.exterior.coords])

# # Create a GeoDataFrame
# gdf = gpd.GeoDataFrame([{'geometry': bbox_wgs84}], crs='EPSG:4326')

# # Save the GeoDataFrame to a shapefile
# gdf.to_file('munich_mantova_square.shp')

# print("Shapefile created successfully!")

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


