# In diesem Skript kann man diverse Informationen über Rasterdateien herausfinden. Einfach das auskommentieren das man nicht braucht und laufen lassen
# 1. Projektion des Rasters erfragen
# 2. Auflösung des Rasters erfagen
# 3. Bei Bedarf Projektion ändern
    # 3.1. auch projektion ändern, fast das gleiche
# 4. Aufllösung verändern - resampling

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.enums import Resampling
from rasterio.transform import from_origin
import pyproj
from osgeo import gdal
import os



# # 1. Projektion erfragen#######################################################################################
# Öffnen Sie die GeoTIFF-Datei (GeoTIFF-Datei auswählen)
dataset = gdal.Open(r"..\data\SRTM\middle_europe.tif", gdal.GA_ReadOnly) #pfad eingeben


# # Öffnen der Datei bei Verwendung von Github
# dataset = gdal.Open(r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\middle_europe.tif", gdal.GA_ReadOnly) #pfad eingeben

# Überprüfen Sie das Koordinatenreferenzsystem (CRS)
projInfo = dataset.GetProjection()

# ProjInfo gibt die Projektionsinformationen als Text zurück
print("Projektion dgm:", projInfo)

#2. Auflösung eines Rasters erfragen ##########################################################################
# Pfad zur umgewandelten GeoTIFF-Datei (UTM 32N) 
dem_path = r"..\data\SRTM\middle_europe.tif" #pfad eingeben


# # Pfad zur umgewandelten GeoTIFF-Datei (UTM 32N) bei Verwendung von Github
# dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\middle_europe.tif" #pfad eingeben

# Öffnen der GeoTIFF-Datei
with rasterio.open(dem_path) as src:
    # Lesen der Auflösung aus dem GeoTIFF
    resolution = src.res  # Tuple (x_resolution, y_resolution)
    width = src.width 
    height = src.height
    # Drucken Sie die Auflösung und Dimensionen
    print(f"Auflösung dgm: {resolution[0]} x {resolution[1]} Meter oder Grad (je nach Projektion)")
    print(f"Breite: {width} Pixel")
    print(f"Höhe: {height} Pixel")


satellite_path = r'..\data\sentinel-2\Sentinel-2_L2A_B08_(Raw).tiff' #pfad eingeben

# Öffnen der GeoTIFF-Datei
with rasterio.open(satellite_path) as src:
    # Lesen der Auflösung aus dem GeoTIFF
    resolution = src.res  # Tuple (x_resolution, y_resolution)
    width = src.width 
    height = src.height
    # Drucken Sie die Auflösung und Dimensionen
    print(f"Auflösung der sentinel: {resolution[0]} x {resolution[1]} Meter pro Pixel")
    print(f"Breite: {width} Pixel")
    print(f"Höhe: {height} Pixel")


#3. projection ändern ###########################################################################################

# relative Pfade:
input_tiff = r'..\data\SRTM\middle_europe.tif'  # Pfad zur Eingabe-TIFF-Datei (WGS84)
output_tiff = r'..\data\SRTM\utm_middle_europe.tif'  # Pfad zur Ausgabe-TIFF-Datei (UTM 32N)


# # Pfade für Github-Verwendung:
# input_tiff = r'C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\middle_europe.tif'  # Pfad zur Eingabe-TIFF-Datei (WGS84)
# output_tiff = r'C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\utm_middle_europe.tif'  # Pfad zur Ausgabe-TIFF-Datei (UTM 32N)


# Definition der Projektionssysteme
src_crs = 'EPSG:4326'  # WGS84 Koordinatenreferenzsystem
dst_crs = 'EPSG:32632'  # UTM Zone 32N Koordinatenreferenzsystem

# Öffnen des Eingabe-TIFFs
with rasterio.open(input_tiff) as src:
    # Umwandlung von WGS84 nach UTM 32N
    transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })

    # Erstellen und Schreiben des Ausgabe-TIFFs
    with rasterio.open(output_tiff, 'w', **kwargs) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest
            )

print(f"GeoTIFF wurde erfolgreich nach UTM Zone 32N umgewandelt und unter {output_tiff} gespeichert.")

# 4. Resampling ################################################################################################################################################
# Funktion zum Resamplen eines Rasters
def resample_raster(input_path, output_path, target_pixel_size):
    if os.path.exists(output_path):
        os.remove(output_path)  # Löschen Sie die Datei, wenn sie bereits existiert
    
    with rasterio.open(input_path) as src:
        # Zielauflösung basierend auf den gewünschten Pixelgrößen in Metern
        dst_resolution = (target_pixel_size, target_pixel_size)
        
        # Berechnung der neuen Höhe und Breite des Rasters
        new_width = int(src.width * src.res[0] / target_pixel_size)
        new_height = int(src.height * src.res[1] / target_pixel_size)
        
        # Transformationsmatrix für das neue Raster
        transform = from_origin(src.bounds.left, src.bounds.top, target_pixel_size, target_pixel_size)
        
        # Resampling durchführen und das Ergebnis speichern
        with rasterio.open(output_path, 'w+', driver='GTiff',
                           width=new_width,
                           height=new_height,
                           count=src.count,
                           dtype=src.dtypes[0],
                           crs=src.crs,
                           transform=transform,
                           nodata=src.nodata) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i),
                          indexes=i)

# Beispielaufruf der Funktion für das Resampling
input_dgm_path = r'..\data\SRTM\utm_middle_europe.tif'
output_resampled_dgm_path = r'..\data\SRTM\resampled_utm_middle_europe.tif'
target_pixel_size = 185.7689556164  # Ziel-Pixelgröße in Metern

resample_raster(input_dgm_path, output_resampled_dgm_path, target_pixel_size)

print(f"DGM wurde auf die Auflösung der Satellitenbilder resampled und gespeichert unter {output_resampled_dgm_path}.")

