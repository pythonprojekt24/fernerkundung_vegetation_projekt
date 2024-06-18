# To Do: shapefiles in die Raster plotten, Höhenwerte hinzufügen
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, Point, LineString
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

# UTM-Koordinaten der Punkte
points = [(690828.96,5334366.44), (640676.06,5001890.22)] # München - Mantova

# UTM-Zoneninformationen für UTM 32N
# utm_crs = {'init': 'epsg:32632'}
utm_crs = 'EPSG:32632'

# Punkte als GeoDataFrame erstellen
points_gdf = gpd.GeoDataFrame(geometry=[Point(x, y) for x, y in points], crs=utm_crs)

# LineString-Objekt aus den Punkten erstellen
line = LineString(points)

# Linie als GeoDataFrame erstellen
line_gdf = gpd.GeoDataFrame(geometry=[line], crs=utm_crs)

# Speichern der Shapefiles
points_gdf.to_file(r'data\shp\points_muc_mant.shp')
line_gdf.to_file(r'data\shp\line_muc_mant.shp')

# Dateipfade der Sentinel-2 Bänder
nir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B08_(Raw).tiff'
swir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B11_(Raw).tiff'
red_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B04_(Raw).tiff'  # Band 4 für NDVI


# Definieren des gewünschten Ausschnitts
# Geben Sie die Grenzen in den UTM-Koordinaten an (xmin, ymin, xmax, ymax)
minx, miny, maxx, maxy = 640000, 4990000, 700000, 5340000

# Erstellen Sie eine Polygon-Box aus den Grenzen
bbox = box(minx, miny, maxx, maxy)

# Erstellen Sie ein GeoDataFrame
geo = gpd.GeoDataFrame({'geometry': [bbox]}, index=[0], crs=utm_crs)

# Funktion zum Zuschneiden und Speichern des Rasters
def crop_and_save_raster(input_path, output_path, geo):
    with rasterio.open(input_path) as src:
        out_image, out_transform = mask(src, geo.geometry, crop=True)
        out_meta = src.meta

        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})

        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)

# Dateipfade der originalen und zugeschnittenen Raster
nir_band_cropped_path = r'data\sentinel-2\59_Sentinel-2_L2A_B08_(Cropped).tiff'
red_band_cropped_path = r'data\sentinel-2\59_Sentinel-2_L2A_B04_(Cropped).tiff'
swir_band_cropped_path = r'data\sentinel-2\59_Sentinel-2_L2A_B11_(Cropped).tiff'

# Zuschneiden und Speichern der Rasterdateien
crop_and_save_raster(nir_band_path, nir_band_cropped_path, geo)
crop_and_save_raster(red_band_path, red_band_cropped_path, geo)
crop_and_save_raster(swir_band_path, swir_band_cropped_path, geo)

print('Zuschneiden abgeschlossen.')

# UTM-Koordinaten der Punkte (München, Mantova Koordinaten)
points = [(690828.96, 5334366.44), (640676.06, 5001890.22)] 
# LineString Objekt aus den Punkten erstellen
line = LineString(points)

# Funktion zum Speichern als Raster
def save_raster(output_path, data, reference_band_path):
    with rasterio.open(reference_band_path) as ref:
        profile = ref.profile
        profile.update(dtype=rasterio.float32, count=1)

        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(data.astype(rasterio.float32), 1)

# Laden der zugeschnittenen Rasterdateien und Fortsetzen des restlichen Codes
with rasterio.open(nir_band_cropped_path) as nir_band, \
     rasterio.open(red_band_cropped_path) as red_band, \
     rasterio.open(swir_band_cropped_path) as swir_band:

    nir = nir_band.read(1).astype(np.float32) / 65535.0
    red = red_band.read(1).astype(np.float32) / 65535.0
    swir = swir_band.read(1).astype(np.float32) / 65535.0

    crs = nir_band.crs
    transform = nir_band.transform

# Berechnung von NDVI und NDMI
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

# Speichern der berechneten NDVI und NDMI Raster
save_raster(r'data\exported_tif\ndvi_scaled_cropped.tif', NDVI, nir_band_cropped_path)
save_raster(r'data\exported_tif\ndmi_scaled_cropped.tif', NDMI, nir_band_cropped_path)

# Berechnung von NDVI und NDMI entlang der Linie
ndvi_values = []
ndmi_values = []
x_values = []

# Interpolieren entlang der Linie
for distance in np.linspace(0, line.length, 500):
    point = line.interpolate(distance)
    col, row = ~transform * (point.x, point.y)
    ndvi = (nir[int(row), int(col)] - red[int(row), int(col)]) / (nir[int(row), int(col)] + red[int(row), int(col)])
    ndmi = (nir[int(row), int(col)] - swir[int(row), int(col)]) / (nir[int(row), int(col)] + swir[int(row), int(col)])
    ndvi_values.append(ndvi)
    ndmi_values.append(ndmi)
    x_values.append(distance)

# Plotten der NDVI und NDMI entlang der Linie
plt.figure(figsize=(10, 6))
plt.plot(x_values, ndvi_values, label='NDVI')
plt.plot(x_values, ndmi_values, label='NDMI')
plt.xlabel('Distanz Muc - Ver (m)')
plt.ylabel('Werte')
plt.title('NDVI und NDMI entlang des Transekts München - Verona (500 Punkte)')
plt.legend()
plt.grid(True)
plt.show()

print('done.')


