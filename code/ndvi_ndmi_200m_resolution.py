#Dieser shit geht nicht
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import geopandas as gpd
from rasterio.enums import Resampling

# Funktion zur Neuabtastung eines Bands auf eine bestimmte Pixelgröße
def resample_band(band_path, new_resolution):
    with rasterio.open(band_path) as src:
        transform, width, height = rasterio._warp._calculate_default_transform(
            src.crs, src.crs, src.width, src.height, *src.bounds, resolution=new_resolution)
        
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': src.crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        data = src.read(
            out_shape=(src.count, height, width),
            resampling=Resampling.bilinear
        )
    return data, transform, src.crs

# UTM-Koordinaten der Punkte
points = [(644748.85, 5083772.51), (500900.42, 5300334.10)] # Bodensee (Konstanz?) bis Riva

# UTM-Zoneninformationen für UTM 32N
utm_crs = 'EPSG:32632'

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

# Neuabtasten der Sentinel-2 Bänder auf 200m Pixelgröße
nir_resampled, transform, crs = resample_band(nir_band_path, 200)
red_resampled, _, _ = resample_band(red_band_path, 200)
swir_resampled, _, _ = resample_band(swir_band_path, 200)

# Berechnung von NDVI und NDMI für das Plot
mask = nir_resampled + red_resampled == 0  # Maske für Divisionen durch Null
NDVI = np.where(mask, np.nan, (nir_resampled - red_resampled) / (nir_resampled + red_resampled))
NDMI = np.where(mask, np.nan, (nir_resampled - swir_resampled) / (nir_resampled + swir_resampled))

# Plotten der NDVI und NDMI
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

ax1.set_title('NDVI')
ndvi_plot = ax1.imshow(NDVI[0], cmap='RdYlGn', vmin=-1, vmax=1)  # NDVI[0] für die erste Bildebene
fig.colorbar(ndvi_plot, ax=ax1)

ax2.set_title('NDMI')
ndmi_plot = ax2.imshow(NDMI[0], cmap='RdYlBu', vmin=-1, vmax=1)  # NDMI[0] für die erste Bildebene
fig.colorbar(ndmi_plot, ax=ax2)

plt.show()

# Funktion zum Speichern als Raster
def save_raster(output_path, data, transform, crs):
    profile = {
        'driver': 'GTiff',
        'dtype': rasterio.float32,
        'nodata': np.nan,
        'width': data.shape[2],
        'height': data.shape[1],
        'count': 1,
        'crs': crs,
        'transform': transform
    }
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)

# Speichern als Raster mit 200m Auflösung
save_raster(r'data\exported_tif\ndvi_200m.tif', NDVI, transform, crs)
save_raster(r'data\exported_tif\ndmi_200m.tif', NDMI, transform, crs)

print('NDVI und NDMI mit 200m Auflösung gespeichert')


print('NDVI und NDMI mit 200m Auflösung gespeichert')

# Berechnung von NDVI und NDMI entlang der Linie
ndvi_values = []
ndmi_values = []
x_values = []

# Entlang der Linie interpolieren
for distance in np.linspace(0, line.length, 500):
    point = line.interpolate(distance)
    col, row = ~transform * (point.x, point.y)  # Umkehrung der Transformationskoordinaten
    ndvi = (nir_resampled[0, int(row), int(col)] - red_resampled[0, int(row), int(col)]) / (nir_resampled[0, int(row), int(col)] + red_resampled[0, int(row), int(col)])
    ndmi = (nir_resampled[0, int(row), int(col)] - swir_resampled[0, int(row), int(col)]) / (nir_resampled[0, int(row), int(col)] + swir_resampled[0, int(row), int(col)])
    ndvi_values.append(ndvi)
    ndmi_values.append(ndmi)
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

print('Done.')
