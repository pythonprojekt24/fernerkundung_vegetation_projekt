# To Do: shapefiles in die Raster plotten, Höhenwerte hinzufügen
from cgitb import text
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, Point, LineString
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import argparse
import fiona

#### PARSER ########################################################################
## python code\vegetation_indices_over_transect.py -startpunkt München -endpunkt Mantova -x_start 690828.96 -y_start 5334366.44 -x_end 640676.06 -y_end 5001890.22 -num_points 3000 
# z.B. Muc - IbK: python code\vegetation_indices_over_transect.py -startpunkt München -endpunkt Innsbruck -x_start 690828.96 -y_start 5334366.44 -x_end 681849.02 -y_end 5237884.63 -num_points 1000 
# Argumentenparser erstellen
parser = argparse.ArgumentParser(description="In diesem Skript können Koordinaten von zwei Orten angegeben werden, die zwischen München und Mantova liegen, um für diese NDVI und NDMI zu berechnen.")

# Argumente definieren
parser.add_argument('-startpunkt', type=str, default="München", help='Name des Startortes')
parser.add_argument('-endpunkt', type=str, default="Mantova", help='Name des Endortes')
parser.add_argument('-x_start', type=float, default=690828.96, help='position of x-coordinate at the starting point')
parser.add_argument('-y_start', type=float, default=5334366.44, help='position of y-coordinate at the starting point')
parser.add_argument('-x_end', type=float, default=640676.06, help='position of x-coordinate at the ending point')
parser.add_argument('-y_end', type=float, default=5001890.22, help='position of y-coordinate at the ending point')
parser.add_argument('-num_points', type=int, default=2000, help='number of points along the transect')

# Argumente parsen
args = parser.parse_args() # oben definiert Argumente werden an Variable args übergeben
####################################################################################################
# Funktion zur Extraktion der Rasterwerte entlang der Linie
def extract_raster_values_along_line(line, dem, dem_transform, dem_nodata, nir, red, swir, raster_transform, num_points):
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
points_gdf.to_file(r'data\shp\points_muc_mant.shp')
line_gdf.to_file(r'data\shp\line_muc_mant.shp')

# Dateipfade der Sentinel-2 Bänder und dem
nir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B08_(Raw).tiff'
swir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B11_(Raw).tiff'
red_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B04_(Raw).tiff' 
#dem_path = r"data\SRTM\resampled_merged_dem_utm.tif"
dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\resampled_merged_dem_utm.tif"


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
#dem_path_cropped = r"data\SRTM\cropped_resampled_merged_dem_utm.tif"
dem_path_cropped = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\cropped_resampled_merged_dem_utm.tif"

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

plt.savefig(r"plots\ndvi_ndmi_raster.png")
plt.show()

# Speichern der berechneten NDVI und NDMI Raster
save_raster(r'data\exported_tif\ndvi_scaled_cropped.tif', NDVI, nir_band_cropped_path)
save_raster(r'data\exported_tif\ndmi_scaled_cropped.tif', NDMI, nir_band_cropped_path)

## Auslesen der Rasterwerte ins Shapefile ################################
num_points = args.num_points
shapefile_path = r'data\shp\line_muc_mant.shp'
line_gdf = gpd.read_file(shapefile_path)
line = line_gdf.geometry.iloc[0]

# Pfad zum DGM und den zusätzlichen Rasterdateien (z.B. NDVI, NDMI)
# dem_path = r"data\SRTM\cropped_resampled_merged_dem_utm.tif"
dem_path = dem_path_cropped
nir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B08_(Cropped).tiff'
red_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B04_(Cropped).tiff'
swir_band_path = r'data\sentinel-2\59_Sentinel-2_L2A_B11_(Cropped).tiff'

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

# Punkte und Rasterwerte entlang der Linie extrahieren
points, elevations, ndvi_values, ndmi_values = extract_raster_values_along_line(
    line, dem, dem_transform, dem_nodata, nir, red, swir, raster_transform, num_points)

# Erstellen eines GeoDataFrames mit den Punkten und den extrahierten Werten
points_gdf = gpd.GeoDataFrame({
    'geometry': points,
    'elevation': elevations,
    'ndvi': ndvi_values,
    'ndmi': ndmi_values
}, crs=line_gdf.crs)

# Speichern des neuen Shapefiles
output_shapefile_path = r"data\shp\points_muc_mant_with_raster_values.shp"
points_gdf.to_file(output_shapefile_path)

print('Shapefile mit Punkten und Rasterwerten gespeichert.')
x_values = np.linspace(0, line.length, len(points_gdf))  # Annahme: gleiche Anzahl von Punkten


# Berechnung der Korrelationskoeffizienten
pearson_corr_ndvi_dem, _ = pearsonr(ndvi_values, elevations)
spearman_corr_ndvi_dem, _ = spearmanr(ndvi_values, elevations)



# Plotten von NDVI, NDMI und DEM entlang der Linie
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot für NDVI und NDMI
line1, = ax1.plot(x_values, ndvi_values, label='NDVI', color='g')
line2, = ax1.plot(x_values, ndmi_values, label='NDMI', color='b')
ax1.set_xlabel(f'Distanz {args.startpunkt} - {args.endpunkt} (m)')
ax1.set_ylabel('NDVI und NDMI Werte')
#ax1.legend(loc='upper left')
ax1.grid(True)

# Zweite y-Achse für DEM
ax2 = ax1.twinx()
line3, = ax2.plot(x_values, elevations, label='DEM Höhe', color='brown')
ax2.set_ylabel('DEM Höhe (m)')
#ax2.legend(loc='upper right')
ax2.yaxis.set_label_position("right")
ax2.yaxis.label.set_rotation(270)
ax2.yaxis.label.set_verticalalignment('bottom')

# Legende hinzufügen
lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
legend = ax1.legend(lines, labels, loc='lower left', fancybox=True, framealpha=1)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_edgecolor('black')

plt.title(f'NDVI, NDMI und DEM entlang des Transekts {args.startpunkt} - {args.endpunkt} ({args.num_points} Punkte)')
plt.savefig(r"plots\ndvi_ndmi_dem_lineplot.png")
plt.show()
print('Linienplot done.')


## Plot mit Punkten
# Plotten der NDVI, NDMI und DEM Punkte entlang der Linie
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot für NDVI und NDMI
line1 = ax1.scatter(x_values, ndvi_values, label='NDVI', color='g', marker='o')
line2 = ax1.scatter(x_values, ndmi_values, label='NDMI', color='b', marker='o')
ax1.set_xlabel(f'Distanz {args.startpunkt} - {args.endpunkt} (m)')
ax1.set_ylabel('NDVI und NDMI Werte')
# ax1.legend(loc='upper left')
ax1.grid(True)

# Zweite y-Achse für DEM
ax2 = ax1.twinx()
line3 = ax2.scatter(x_values, elevations, label='DEM Höhe', color='brown', marker='o')
ax2.set_ylabel('DEM Höhe (m)')
ax2.yaxis.set_label_position("right")
ax2.yaxis.label.set_rotation(270)
ax2.yaxis.label.set_verticalalignment('bottom')
#ax2.legend(loc='upper right')

lines = [line1, line2, line3]
labels = [line.get_label() for line in lines]
legend = ax1.legend(lines, labels, loc='lower left', fancybox=True, framealpha=1)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_edgecolor('black')

# Anzeige der Korrelationskoeffizienten im Plot
plt.text(0.5, 0.90, f'Spearman Korrelation NDVI-DEM: {spearman_corr_ndvi_dem:.2f}', ha='center', va='center', transform=ax1.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
plt.text(0.5, 0.95, f'Pearson Korrelation NDVI-DEM: {pearson_corr_ndvi_dem:.2f}', ha='center', va='center', transform=ax1.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

plt.title(f'NDVI, NDMI und DEM entlang des Transekts {args.startpunkt} - {args.endpunkt} ({args.num_points} Punkte)')
plt.savefig(r"plots\ndvi_ndmi_dem_plot.png")
plt.show()


print('done.')

# BOXPLOTS
# Höhenklassen definieren
hoehenklassen = np.arange(0, 3000, 200)  # z.B. Klassen von 0 bis 3000m in 200m Schritten
hoehenlabels = [f'{hoehenklassen[i]}-{hoehenklassen[i+1]}' for i in range(len(hoehenklassen)-1)]

# NDVI-Werte nach Höhenklassen gruppieren
hoehen_ndvi_dict = {label: [] for label in hoehenlabels}
for ndvi, dem_value in zip(ndvi_values, elevations):
    for i in range(len(hoehenklassen)-1):
        if hoehenklassen[i] <= dem_value < hoehenklassen[i+1]:
            hoehen_ndvi_dict[hoehenlabels[i]].append(ndvi)
            break

# NDVI-Werte nach Höhenklassen gruppieren
hoehen_ndmi_dict = {label: [] for label in hoehenlabels}
for ndmi, dem_value in zip(ndmi_values, elevations):
    for i in range(len(hoehenklassen)-1):
        if hoehenklassen[i] <= dem_value < hoehenklassen[i+1]:
            hoehen_ndmi_dict[hoehenlabels[i]].append(ndmi)
            break

# Boxplot der NDVI-Werte nach Höhenklassen
fig, ax = plt.subplots(figsize=(14, 8))
box_colors = plt.cm.viridis(np.linspace(0, 1, len(hoehenlabels)))
box = ax.boxplot([hoehen_ndvi_dict[label] for label in hoehenlabels], labels=hoehenlabels, patch_artist=True, showfliers=False)
for patch, color in zip(box['boxes'], box_colors):
    patch.set_facecolor(color)
for median in box['medians']:
    median.set(color='yellow', linewidth=2)
means = [np.mean(hoehen_ndvi_dict[label]) for label in hoehenlabels]
ax.plot(range(1, len(hoehenlabels) + 1), means, marker='o', color='white', linestyle='none', markersize=6, label='Mean')
ax.set_xlabel('Höhenklassen (m)', fontsize=14, fontweight='bold')
ax.set_ylabel('NDVI', fontsize=14, fontweight='bold')
ax.set_title('Verteilung der NDVI-Werte nach Höhenklassen', fontsize=16, fontweight='bold')
plt.xticks(rotation=45, fontsize=12)
ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
ax.set_facecolor('#f7f7f7')
plt.legend()
plt.tight_layout()
plt.savefig(r"plots\ndvi_height_boxplot.png")
plt.show()

# Boxplot der NDMI-Werte nach Höhenklassen
fig, ax = plt.subplots(figsize=(14, 8))
box_colors = plt.cm.viridis(np.linspace(0, 1, len(hoehenlabels)))
box = ax.boxplot([hoehen_ndmi_dict[label] for label in hoehenlabels], labels=hoehenlabels, patch_artist=True, showfliers=False)
for patch, color in zip(box['boxes'], box_colors):
    patch.set_facecolor(color)
for median in box['medians']:
    median.set(color='yellow', linewidth=2)
means = [np.mean(hoehen_ndmi_dict[label]) for label in hoehenlabels]
ax.plot(range(1, len(hoehenlabels) + 1), means, marker='o', color='white', linestyle='none', markersize=6, label='Mean')
ax.set_xlabel('Höhenklassen (m)', fontsize=14, fontweight='bold')
ax.set_ylabel('NDMI', fontsize=14, fontweight='bold')
ax.set_title('Verteilung der NDMI-Werte nach Höhenklassen', fontsize=16, fontweight='bold')
plt.xticks(rotation=45, fontsize=12)
ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)
ax.set_facecolor('#f7f7f7')
plt.legend()
plt.tight_layout()
plt.savefig(r"plots\ndmi_height_boxplot.png")
plt.show()