import rasterio

# Pfade zu deiner Rasterdatei
dem_path = r"C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\cropped_resampled_merged_dem_utm.tif"

# Öffnen der Rasterdatei
with rasterio.open(dem_path) as dem_band:
    # Überprüfen der Metadaten
    profile = dem_band.profile

    # Überprüfen des nodata-Werts
    if profile['nodata'] is not None:
        nodata_value = profile['nodata']
        print(f"Der nodata-Wert in der Rasterdatei ist: {nodata_value}")
    else:
        print("Die Rasterdatei enthält keine explizite nodata-Information.")
