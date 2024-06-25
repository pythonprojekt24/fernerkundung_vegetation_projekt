import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import LineString, Point

# Laden des Shapefiles
shapefile_path = r'data\shp\line_muc_mant.shp'
# Pfad zum DGM
dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\cropped_resampled_merged_dem_utm.tif"

line_gdf = gpd.read_file(shapefile_path)
line = line_gdf.geometry.iloc[0]

# Laden des DGM
with rasterio.open(dem_path) as dem_band:
    dem = dem_band.read(1).astype(np.float32)
    dem_nodata = dem_band.nodata
    transform = dem_band.transform

# Funktion zur Extraktion von Rasterwerten entlang der Linie
def extract_points_and_rasterdata(line, raster, transform, raster_nodata, num_points=2000):
    points = []
    raster_values = []
    distances = np.linspace(0, line.length, num_points)
    for distance in distances:
        point = line.interpolate(distance)
        col, row = ~transform * (point.x, point.y)
        col, row = int(round(col)), int(round(row))
        if (0 <= row < raster.shape[0]) and (0 <= col < raster.shape[1]):
            value = raster[row, col]
            if value != raster_nodata:
                points.append(point)
                raster_values.append(value)
    return points, raster_values

# # Funktion zur Extraktion der Höhenwerte entlang der Linie
# def extract_points_and_elevations(line, dem, transform, dem_nodata, num_points=2000):
#     points = []
#     elevations = []
#     distances = np.linspace(0, line.length, num_points)
#     for distance in distances:
#         point = line.interpolate(distance)
#         col, row = ~transform * (point.x, point.y)
#         col, row = int(round(col)), int(round(row))
#         if (0 <= row < dem.shape[0]) and (0 <= col < dem.shape[1]):
#             dem_value = dem[row, col]
#             if dem_value != dem_nodata:
#                 points.append(point)
#                 elevations.append(dem_value)
#     return points, elevations

# Punkte und Höhenwerte entlang der Linie extrahieren
points, elevations = extract_points_and_rasterdata(line, dem, transform, dem_nodata)

# Erstellen eines GeoDataFrames mit den Punkten und Höhenwerten
points_gdf = gpd.GeoDataFrame({
    'geometry': points,
    'elevation': elevations
}, crs=line_gdf.crs)

# Speichern des neuen Shapefiles
output_shapefile_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\points_muc_mant_with_elevation.shp"
points_gdf.to_file(output_shapefile_path)

print('Shapefile mit Punkten und Höhenwerten gespeichert.')
