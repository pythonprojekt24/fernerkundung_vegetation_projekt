# einlesen der dem kacheln die ich im vorhinein manuell downgeloaded habe
import numpy as np
import rasterio
from rasterio.merge import merge
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import pyproj


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

# Übernehmen der Metadaten von der ersten Kachel und diese anpassen an das zusammengeführte Array
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

print("merging done")

############## reproject ###################

def reproject_geotiff(src_path, dst_path, dst_crs):
    with rasterio.open(src_path) as src:
        # Get the source CRS
        src_crs = src.crs
        
        # Calculate the transform and dimensions of the destination
        transform, width, height = calculate_default_transform(
            src_crs, dst_crs, src.width, src.height, *src.bounds)
        
        # Define the metadata for the destination file
        dst_meta = src.meta.copy()
        dst_meta.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        
        with rasterio.open(dst_path, 'w', **dst_meta) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
            print(f"Reprojection completed successfully. Output saved to {dst_path}")

# hier kann man direkt das "modul", also die Funktion, ausführen. Oder man macht es in einem anderen Skript
if __name__ == "__main__":
    src_tiff = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\merged_dem.tif"  # Pfad zur Eingabedatei
    dst_tiff = 'dem_dir / "reprojected32632_merged_dem.tif'  # Pfad zur Ausgabedatei
    
    # UTM Zone bestimmen (z.B. UTM Zone 32N)
    # pyproj.CRS.from_epsg() verwenden, um eine CRS-Definition zu erhalten.
    # Beispiel für UTM Zone 32N: epsg:32632
    dst_crs = pyproj.CRS.from_epsg(32632)
    
    reproject_geotiff(src_tiff, dst_tiff, dst_crs)


print("done")
