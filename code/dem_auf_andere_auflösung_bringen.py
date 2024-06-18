import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
import os

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
input_dgm_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\merged_dem_utm.tif"
output_resampled_dgm_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\resampled_merged_dem_utm.tif"
target_pixel_size = 185.7689556164  # Ziel-Pixelgröße in Metern

resample_raster(input_dgm_path, output_resampled_dgm_path, target_pixel_size)

print(f"DGM wurde auf die Auflösung der Satellitenbilder resampled und gespeichert unter {output_resampled_dgm_path}.")
