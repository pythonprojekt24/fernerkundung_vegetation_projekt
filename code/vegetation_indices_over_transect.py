# To Do: shapefiles in die Raster plotten, Höhenwerte hinzufügen
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, Point, LineString
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import argparse

#### PARSER ########################################################################
## python ndvi_ndmi_mit_dem_muc_mantova.py -x_start 690828.96 -y_start 5334366.44 -x_end 640676.06 -y_end 5001890.22
# z.B. Muc - IbK: python ndvi_ndmi_mit_dem_muc_mantova.py -x_start 690828.96 -y_start 5334366.44 -x_end 681849.02 -y_end 5237884.63
# Argumentenparser erstellen
parser = argparse.ArgumentParser(description="In diesem Skript können Koordinaten von zwei Orten angegeben werden, die zwischen München und Mantova liegen, um für diese NDVI und NDMI zu berechnen.")

# Argumente definieren
parser.add_argument('-x_start', type=float, default=690828.96, help='position of x-coordinate at the starting point')
parser.add_argument('-y_start', type=float, default=5334366.44, help='position of y-coordinate at the starting point')
parser.add_argument('-x_end', type=float, default=640676.06, help='position of x-coordinate at the ending point')
parser.add_argument('-y_end', type=float, default=5001890.22, help='position of y-coordinate at the ending point')

# Argumente parsen
args = parser.parse_args() # oben definiert Argumente werden an Variable args übergeben
####################################################################################################

# UTM-Koordinaten der Punkte
# points = [(690828.96,5334366.44), (640676.06,5001890.22)] # München - Mantova
points =[(args.x_start,args.y_start),(args.x_end, args.y_end)] # entweder diese Zeile verwenden für Parser oder die darüber für Muc-Mant


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
points_gdf.to_file(r'..\data\shp\points_muc_mant.shp')
line_gdf.to_file(r'..\data\shp\line_muc_mant.shp')

# Dateipfade der Sentinel-2 Bänder und dem
nir_band_path = r'..\data\sentinel-2\59_Sentinel-2_L2A_B08_(Raw).tiff'
swir_band_path = r'..\data\sentinel-2\59_Sentinel-2_L2A_B11_(Raw).tiff'
red_band_path = r'..\data\sentinel-2\59_Sentinel-2_L2A_B04_(Raw).tiff' 
dem_path = r"..\data\SRTM\resampled_merged_dem_utm.tif"
# dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\resampled_merged_dem_utm.tif"


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
nir_band_cropped_path = r'..\data\sentinel-2\59_Sentinel-2_L2A_B08_(Cropped).tiff'
red_band_cropped_path = r'..\data\sentinel-2\59_Sentinel-2_L2A_B04_(Cropped).tiff'
swir_band_cropped_path = r'..\data\sentinel-2\59_Sentinel-2_L2A_B11_(Cropped).tiff'
dem_path_cropped = r"..\data\SRTM\cropped_resampled_merged_dem_utm.tif"
#dem_path_cropped = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\cropped_resampled_merged_dem_utm.tif"

# Zuschneiden und Speichern der Rasterdateien
crop_and_save_raster(nir_band_path, nir_band_cropped_path, geo)
crop_and_save_raster(red_band_path, red_band_cropped_path, geo)
crop_and_save_raster(swir_band_path, swir_band_cropped_path, geo)
crop_and_save_raster(dem_path, dem_path_cropped, geo)

print('Zuschneiden abgeschlossen.')

# UTM-Koordinaten der Punkte (München, Mantova Koordinaten)
# points = [(690828.96, 5334366.44), (640676.06, 5001890.22)] 
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
     rasterio.open(swir_band_cropped_path) as swir_band,\
     rasterio.open(dem_path_cropped) as dem_band:

    nir = nir_band.read(1).astype(np.float32) / 65535.0
    red = red_band.read(1).astype(np.float32) / 65535.0
    swir = swir_band.read(1).astype(np.float32) / 65535.0
    dem = dem_band.read(1).astype(np.float32)  # DGM Daten einlesen
    dem_nodata = -32767.0  # Nodata Wert für DEM

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
save_raster(r'..\data\exported_tif\ndvi_scaled_cropped.tif', NDVI, nir_band_cropped_path)
save_raster(r'..\data\exported_tif\ndmi_scaled_cropped.tif', NDMI, nir_band_cropped_path)

# Berechnung von NDVI und NDMI entlang der Linie
ndvi_values = []
ndmi_values = []
dem_values = []
x_values = []

# to do: punkte checken
for distance in np.linspace(0, line.length, 2000):
    point = line.interpolate(distance)
    col, row = ~transform * (point.x, point.y)

    if (0 <= int(row) < nir.shape[0]) and (0 <= int(col) < nir.shape[1]):
        ndvi = (nir[int(row), int(col)] - red[int(row), int(col)]) / (nir[int(row), int(col)] + red[int(row), int(col)])
        ndmi = (nir[int(row), int(col)] - swir[int(row), int(col)]) / (nir[int(row), int(col)] + swir[int(row), int(col)])
        dem_value = dem[int(row), int(col)]

        # Filtern von NA-Werten
        if dem_value != dem_nodata:
            ndvi_values.append(ndvi)
            ndmi_values.append(ndmi)
            dem_values.append(dem_value)
            x_values.append(distance)
        else:
            # Hier werden keine Werte hinzugefügt, nur die Lücke in der Linie markiert
            pass
    else:
        #Lücke hinzufügen
        pass

# Berechnung der Korrelationskoeffizienten
pearson_corr_ndvi_dem, _ = pearsonr(ndvi_values, dem_values)
spearman_corr_ndvi_dem, _ = spearmanr(ndvi_values, dem_values)

# Plotten von NDVI, NDMI und DEM entlang der Linie
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot für NDVI und NDMI
ax1.plot(x_values, ndvi_values, label='NDVI', color='g')
ax1.plot(x_values, ndmi_values, label='NDMI', color='b')
ax1.set_xlabel('Distanz Muc - Ver (m)')
ax1.set_ylabel('NDVI und NDMI Werte')
ax1.legend(loc='upper left')
ax1.grid(True)

# Zweite y-Achse für DEM
ax2 = ax1.twinx()
ax2.plot(x_values, dem_values, label='DEM Höhe', color='r')
ax2.set_ylabel('DEM Höhe (m)')
ax2.legend(loc='upper right')

plt.title('Linienplot NDVI, NDMI und DEM entlang des Transekts München - Mantova (100 Punkte)')
plt.show()

print('Linienplot done.')

# Plotten der NDVI, NDMI und DEM Punkte entlang der Linie
fig, ax1 = plt.subplots(figsize=(10, 6))

# Scatter Plot für NDVI und NDMI
ax1.scatter(x_values, ndvi_values, label='NDVI', color='g', marker='o')
ax1.scatter(x_values, ndmi_values, label='NDMI', color='b', marker='o')
ax1.set_xlabel('Distanz Muc - Ver (m)')
ax1.set_ylabel('NDVI und NDMI Werte')
ax1.legend(loc='upper left')
ax1.grid(True)

# Zweite y-Achse für DEM
ax2 = ax1.twinx()
ax2.scatter(x_values, dem_values, label='DEM Höhe', color='r', marker='o')
ax2.set_ylabel('DEM Höhe (m)')
ax2.legend(loc='upper right')

# Anzeige der Korrelationskoeffizienten im Plot
plt.text(0.5, 0.95, f'Pearson Korrelation NDVI-DEM: {pearson_corr_ndvi_dem:.2f}', ha='center', va='center', transform=ax1.transAxes, fontsize=10)
plt.text(0.5, 0.90, f'Spearman Korrelation NDVI-DEM: {spearman_corr_ndvi_dem:.2f}', ha='center', va='center', transform=ax1.transAxes, fontsize=10)


plt.title('NDVI, NDMI und DEM Punkte entlang des Transekts München - Mantova (100 Punkte)')
plt.show()

print('done.')

# To do: Wie viele Prozent der NDVI werte sind in welchen Höhenklassen? --> hypsographische kurve ... boxplot  --> also wie sind die NDVI und NDMI auf gewisse Höhenstufen 
# verteilt?
# Die Linie bzw. Punkte checken wo die Werte interpoliert werden ... ist das wircklich die richtige Methode? 
# # to do: punkte checken
# for distance in np.linspace(startpunkt x Koordinate, endpunkt x Koordinate, 2000): --> und das gleiche auf mit y Anfang und x Ende
#     point = line.interpolate(distance)
#     col, row = ~transform * (point.x, point.y)

