import rasterio
from rasterio.enums import Resampling

# Funktion zum Resamplen eines Rasters
def resample_raster(input_path, output_path, scale_factor):
    with rasterio.open(input_path) as src:
        # Definiere die Zielauflösung basierend auf dem Skalierungsfaktor
        dst_resolution = (src.res[0] * scale_factor, src.res[1] * scale_factor)
        
        # Resampling durchführen und das Ergebnis speichern
        with rasterio.open(output_path, 'w', driver='GTiff',
                           width=src.width * scale_factor,
                           height=src.height * scale_factor,
                           count=src.count,
                           dtype=src.dtypes[0],
                           crs=src.crs,
                           transform=src.transform * src.transform.scale(scale_factor, scale_factor),
                           nodata=src.nodata) as dst:
            for i in range(1, src.count + 1):
                dst.write(src.read(i),
                          indexes=i)

# Beispielaufruf der Funktion für das Resampling
input_dgm_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\merged_dem_utm.tif"
output_resampled_dgm_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\resampled_merged_dem_utm.tif"
scale_factor = 185.7689556164 / 24.533388521718578  # oder entsprechend für die andere Dimension

resample_raster(input_dgm_path, output_resampled_dgm_path, scale_factor)

print(f"DGM wurde auf die Auflösung der Satellitenbilder resampled und gespeichert unter {output_resampled_dgm_path}.")
