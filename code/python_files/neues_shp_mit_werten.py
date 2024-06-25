import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt


# Laden des Shapefiles mit der Linie
shapefile_path = r'data\shp\line_muc_mant.shp'
line_gdf = gpd.read_file(shapefile_path)
line = line_gdf.geometry.iloc[0]

# Pfad zum DGM und den zusätzlichen Rasterdateien (z.B. NDVI, NDMI)
dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\cropped_resampled_merged_dem_utm.tif"
nir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B08_(Raw).tiff'
red_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B04_(Raw).tiff'
swir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B11_(Raw).tiff'

# Laden des DGM
with rasterio.open(dem_path) as dem_band:
    dem = dem_band.read(1).astype(np.float32)
    dem_nodata = dem_band.nodata
    dem_transform = dem_band.transform

# Laden der zusätzlichen Raster
with rasterio.open(nir_band_path) as nir_band, \
     rasterio.open(red_band_path) as red_band, \
     rasterio.open(swir_band_path) as swir_band:
    nir = nir_band.read(1).astype(np.float32)
    red = red_band.read(1).astype(np.float32)
    swir = swir_band.read(1).astype(np.float32)
    raster_transform = nir_band.transform

print("vor der Funktion")

# Funktion zur Extraktion der Rasterwerte entlang der Linie
def extract_raster_values_along_line(line, dem, dem_transform, dem_nodata, nir, red, swir, raster_transform, num_points=2000):
    points = []
    elevations = []
    ndvi_values = []
    ndmi_values = []
    distances = np.linspace(0, line.length, num_points)
    for distance in distances:
        point = line.interpolate(distance)
        dem_col, dem_row = ~dem_transform * (point.x, point.y)
        raster_col, raster_row = ~raster_transform * (point.x, point.y)
        dem_col, dem_row = int(round(dem_col)), int(round(dem_row))
        raster_col, raster_row = int(round(raster_col)), int(round(raster_row))
        
        if (0 <= dem_row < dem.shape[0]) and (0 <= dem_col < dem.shape[1]):
            dem_value = dem[dem_row, dem_col]
            if dem_value != dem_nodata:
                points.append(point)
                elevations.append(dem_value)
                
                if (0 <= raster_row < nir.shape[0]) and (0 <= raster_col < nir.shape[1]):
                    nir_value = nir[raster_row, raster_col]
                    red_value = red[raster_row, raster_col]
                    swir_value = swir[raster_row, raster_col]
                    
                    ndvi = (nir_value - red_value) / (nir_value + red_value) if (nir_value + red_value) != 0 else np.nan
                    ndmi = (nir_value - swir_value) / (nir_value + swir_value) if (nir_value + swir_value) != 0 else np.nan
                    
                    ndvi_values.append(ndvi)
                    ndmi_values.append(ndmi)
                else:
                    ndvi_values.append(np.nan)
                    ndmi_values.append(np.nan)
    return points, elevations, ndvi_values, ndmi_values


# Punkte und Rasterwerte entlang der Linie extrahieren
points, elevations, ndvi_values, ndmi_values = extract_raster_values_along_line(
    line, dem, dem_transform, dem_nodata, nir, red, swir, raster_transform)

# Erstellen eines GeoDataFrames mit den Punkten und den extrahierten Werten
points_gdf = gpd.GeoDataFrame({
    'geometry': points,
    'elevation': elevations,
    'ndvi': ndvi_values,
    'ndmi': ndmi_values
}, crs=line_gdf.crs)

# Speichern des neuen Shapefiles
output_shapefile_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\points_muc_mant_with_raster_values.shp"
points_gdf.to_file(output_shapefile_path)

print('Shapefile mit Punkten und Rasterwerten gespeichert.')

# Laden des Shapefiles mit den Punkten und den extrahierten Werten
points_gdf = gpd.read_file(r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\points_muc_mant_with_raster_values.shp")

# Extrahieren der Werte
distances = np.linspace(0, line.length, len(points_gdf))  # Annahme: gleiche Anzahl von Punkten
elevations = points_gdf['elevation'].values
ndvi_values = points_gdf['ndvi'].values
ndmi_values = points_gdf['ndmi'].values

# Plot erstellen
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot für Höhe (elevation)
ax1.plot(distances, elevations, label='Höhe (Elevation)', color='r')
ax1.set_xlabel('Distanz entlang der Linie (m)')
ax1.set_ylabel('Höhe (m)', color='r')
ax1.tick_params(axis='y', labelcolor='r')
ax1.legend(loc='upper left')

# Zweite y-Achse für NDVI und NDMI
ax2 = ax1.twinx()
ax2.plot(distances, ndvi_values, label='NDVI', color='g')
ax2.plot(distances, ndmi_values, label='NDMI', color='b')
ax2.set_ylabel('NDVI und NDMI Werte')
ax2.tick_params(axis='y')
ax2.legend(loc='upper right')

plt.title('Höhe, NDVI und NDMI entlang der Linie')
plt.grid(True)
plt.show()

# Plot erstellen
fig, ax1 = plt.subplots(figsize=(10, 6))

# Scatter Plot für NDVI und NDMI
ax1.scatter(distances, ndvi_values, label='NDVI ', color='g', marker='o')
ax1.scatter(distances, ndmi_values, label='NDMI', color='b', marker='o')
ax1.set_xlabel('Distanz Muc - Ver (m)')
ax1.set_ylabel('NDVI und NDMI Werte')
ax1.legend(loc='upper left')
ax1.grid(True)

# Zweite y-Achse für DEM
ax2 = ax1.twinx()
ax2.scatter(distances, elevations, label='DEM Höhe', color='r', marker='o')
ax2.set_ylabel('DEM Höhe (m)')
ax2.legend(loc='upper right')

plt.title('NDVI, NDMI und DEM Punkte entlang des Transekts München - Mantova (2000 Punkte)')
plt.show()

