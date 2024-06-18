import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import pyproj

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
    src_tiff = 'input.tif'  # Pfad zur Eingabedatei
    dst_tiff = 'output_projected.tif'  # Pfad zur Ausgabedatei
    
    # UTM Zone bestimmen (z.B. UTM Zone 32N)
    # pyproj.CRS.from_epsg() verwenden, um eine CRS-Definition zu erhalten.
    # Beispiel für UTM Zone 32N: epsg:32632
    dst_crs = pyproj.CRS.from_epsg(32632)
    
    reproject_geotiff(src_tiff, dst_tiff, dst_crs)
