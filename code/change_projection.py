# In diesem Skript kann man diverse Informationen über Rasterdatein herausfinden. Einfach das auskommentieren das man nicht braucht und laufen lassen
# 1. Projektion des Rasters erfragen
# 2. Auflösung des Rasters erfagen
# 3. Bei Bedarf Projektion ändern

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import pyproj
from osgeo import gdal

# 1. Projektion erfragen#######################################################################################
# Öffnen Sie die GeoTIFF-Datei
dataset = gdal.Open(r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\middle_europe.tif", gdal.GA_ReadOnly)

# Überprüfen Sie das Koordinatenreferenzsystem (CRS)
projInfo = dataset.GetProjection()

# ProjInfo gibt die Projektionsinformationen als Text zurück
print("Projektion dgm:", projInfo)

#2. Auflösung eines Rasters erfragen ##########################################################################
# Pfad zur umgewandelten GeoTIFF-Datei (UTM 32N)
dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\middle_europe.tif"

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


satellite_path = r'data\sentinel-2\Sentinel-2_L2A_B08_(Raw).tiff'

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

# def reproject_geotiff(src_path, dst_path, dst_crs):
#     with rasterio.open(src_path) as src:
#         # Get the source CRS
#         src_crs = src.crs
        
#         # Calculate the transform and dimensions of the destination
#         transform, width, height = calculate_default_transform(
#             src_crs, dst_crs, src.width, src.height, *src.bounds)
        
#         # Define the metadata for the destination file
#         dst_meta = src.meta.copy()
#         dst_meta.update({
#             'crs': dst_crs,
#             'transform': transform,
#             'width': width,
#             'height': height
#         })
        
#         with rasterio.open(dst_path, 'w', **dst_meta) as dst:
#             for i in range(1, src.count + 1):
#                 reproject(
#                     source=rasterio.band(src, i),
#                     destination=rasterio.band(dst, i),
#                     src_transform=src.transform,
#                     src_crs=src_crs,
#                     dst_transform=transform,
#                     dst_crs=dst_crs,
#                     resampling=Resampling.nearest)
#             print(f"Reprojection completed successfully. Output saved to {dst_path}")

# # hier kann man direkt das "modul", also die Funktion, ausführen. Oder man macht es in einem anderen Skript
# if __name__ == "__main__":
#     src_tiff = 'input.tif'  # Pfad zur Eingabedatei
#     dst_tiff = 'output_projected.tif'  # Pfad zur Ausgabedatei
    
#     # UTM Zone bestimmen (z.B. UTM Zone 32N)
#     # pyproj.CRS.from_epsg() verwenden, um eine CRS-Definition zu erhalten.
#     # Beispiel für UTM Zone 32N: epsg:32632
#     dst_crs = pyproj.CRS.from_epsg(32632)
    
#     reproject_geotiff(src_tiff, dst_tiff, dst_crs)

print("done")
