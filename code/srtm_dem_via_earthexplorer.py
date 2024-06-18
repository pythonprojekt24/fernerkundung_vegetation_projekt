# einlesen der dem kacheln die ich im vorhinein manuell downgeloaded habe
import numpy as np
import rasterio
from rasterio.merge import merge
from pathlib import Path

# Funktion zum Einlesen der DEM-Kacheln
def read_dem(path_to_dem):
    with rasterio.open(path_to_dem, "r") as img:
        array = img.read(1).astype(np.float32)  # Erstes Band lesen und als float32 konvertieren
        return array, img.transform  # Array und Transformationsmatrix zurückgeben

# Pfad zum Verzeichnis mit den DEM-Kacheln
dem_dir = Path(r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM")

# Liste zum Speichern der geöffneten DEM-Kacheln und ihrer Transformationsinformationen
kacheln = []
metadata_list = []

# Alle .tif-Dateien im Verzeichnis einlesen
for tif in dem_dir.glob("*.tif"):
    print(f"Reading file: {tif}")
    band_array, transform = read_dem(tif)  # DEM-Kachel und Transformationsinformation einlesen
    kacheln.append(band_array)
    metadata_list.append((band_array.shape, transform, tif))  # Metadaten speichern

# Verwenden Sie rasterio.open() und lesen Sie die Kacheln als Rasterio-Datasets
datasets = [rasterio.open(tif) for tif in dem_dir.glob("*.tif")]

# Merge the DEM tiles
merged_array, merged_transform = merge(datasets)

# Übernehmen Sie die Metadaten von der ersten Kachel und passen Sie sie an das zusammengeführte Array an
out_meta = datasets[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "height": merged_array.shape[1],
    "width": merged_array.shape[2],
    "transform": merged_transform
})

# Speichern Sie das zusammengeführte DEM als GeoTIFF
output_path = dem_dir / "merged_dem.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(merged_array)

print(f"Merged DEM saved to {output_path}")


print("done")
