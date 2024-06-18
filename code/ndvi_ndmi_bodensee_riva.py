# To Do: shapefiles in die Raster plotten, Höhenwerte hinzufügen
# EPSG wichtig! EPSG:32632
# DGM hat EPSG 25832 --> bis 1 m Genauigkeit ok

import rasterio
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import geopandas as gpd


# UTM-Koordinaten der Punkte
points = [(644748.85, 5083772.51), (500900.42, 5300334.10)] # Bodensee (Konstanz?) bis Riva

# UTM-Zoneninformationen für UTM 32N
utm_crs = {'init': 'epsg:32632'}

# Punkte als GeoDataFrame erstellen
points_gdf = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in points], crs=utm_crs)

# LineString-Objekt aus den Punkten erstellen
line = LineString(points)

# Linie als GeoDataFrame erstellen
line_gdf = gpd.GeoDataFrame(geometry=[line], crs=utm_crs)

# Speichern der Shapefiles
points_gdf.to_file(r'data\shp\points_Bodensee_Riva.shp')
line_gdf.to_file(r'data\shp\line_Bodensee_Riva.shp')

# Dateipfade der Sentinel-2 Bänder
nir_band_path = r'data\sentinel-2\Sentinel-2_L2A_B08_(Raw).tiff'
swir_band_path = r'data\sentinel-2\Sentinel-2_L2A_B11_(Raw).tiff'
red_band_path = r'data\sentinel-2\Sentinel-2_L2A_B04_(Raw).tiff'  # Band 4 für NDVI

# Einlesen der Bänder
with rasterio.open(nir_band_path) as nir_band, \
     rasterio.open(red_band_path) as red_band, \
     rasterio.open(swir_band_path) as swir_band:

    nir = nir_band.read(1).astype(np.float32) / 65535.0
    red = red_band.read(1).astype(np.float32) / 65535.0
    swir = swir_band.read(1).astype(np.float32) / 65535.0

    # Extrahiere Koordinatensysteminformationen
    crs = nir_band.crs

    # Extrahiere Transformationsinformationen
    transform = nir_band.transform

# Berechnung von NDVI und NDMI für das Plot
NDVI = (nir - red) / (nir + red)
NDMI = (nir - swir) / (nir + swir)

# Plotten der NDVI und NDMI
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

ax1.set_title('NDVI')
ndvi_plot = ax1.imshow(NDVI, cmap='RdYlGn', vmin=-1, vmax=1)
fig.colorbar(ndvi_plot, ax=ax1)

ax2.set_title('NDMI')
ndmi_plot = ax2.imshow(NDMI, cmap='RdYlBu', vmin=-1, vmax=1)
fig.colorbar(ndmi_plot, ax=ax2)

plt.show()

print ('step 1 done')

# Speichern als Raster
def save_raster(output_path, data, reference_band_path):
    with rasterio.open(reference_band_path) as ref:
        profile = ref.profile
        profile.update(dtype=rasterio.float32, count=1)

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data.astype(rasterio.float32), 1)

save_raster(r'data\exported_tif\ndvi_scaled_cropped.tif', NDVI, nir_band_path)
save_raster(r'data\exported_tif\ndmi_scaled_cropped.tif', NDMI, nir_band_path)

# Berechnung von NDVI und NDMI entlang der Linie
ndvi_values = []
ndmi_values = []
x_values = []

# Entlang der Linie interpolieren
for distance in np.linspace(0, line.length, 500):
    point = line.interpolate(distance)
    col, row = ~transform * (point.x, point.y)  # Umkehrung der Transformationskoordinaten
    ndvi = (nir[int(row), int(col)] - red[int(row), int(col)]) / (nir[int(row), int(col)] + red[int(row), int(col)])
    ndmi = (nir[int(row), int(col)] - swir[int(row), int(col)]) / (nir[int(row), int(col)] + swir[int(row), int(col)])
    # dem = 
    ndvi_values.append(ndvi)
    ndmi_values.append(ndmi)
    # dem_values.append()
    x_values.append(distance)  # Hinzufügen der Entfernung entlang der Linie

# Plotten der NDVI und NDMI entlang der Linie
plt.figure(figsize=(10, 6))
plt.plot(x_values, ndvi_values, label='NDVI')
plt.plot(x_values, ndmi_values, label='NDMI')
plt.xlabel('Distanz Bodensee - Riva (m)')
plt.ylabel('Werte')
plt.title('NDVI und NDMI entlang des Transekts Bodensee - Riva (500 Punkte)')
plt.legend()
plt.grid(True)
plt.show()

print('done.')