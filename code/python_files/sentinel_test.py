# funktioniert leider noch nicht :(

from pystac_client import Client
from odc.stac import load
import odc.geo
import os
import numpy as np

# Verbindet sich mit einem öffentlichen STAC-Katalog
client = Client.open("https://earth-search.aws.element84.com/v1")

# Definiert die Sammlung, aus der die Daten abgerufen werden
collection = "sentinel-2-l2a"

# Definiert die Geometrie des Interessengebiets (ROI) als ein Rechteck mit den Koordinaten für Ulm und Ravenna
muc_lon, muc_lat = 11.574444, 48.139722
mant_lon, mant_lat = 10.791111, 45.156111

#unten links = Mant
#unten rechts = 11.577, 45.1474 .....muc_lon, mant_lat
#oben rechts = muc
#oben links = 10.7983, 48.1267 ........mant_lon, muc_lat

geometry = {
    "type": "Polygon",
    "coordinates": [
        [
            [mant_lon, muc_lat],  # Obere linke Ecke 
            [muc_lon, muc_lat],  # Obere rechte Ecke
            [muc_lon, mant_lat],  # Untere rechte Ecke 
            [mant_lon, mant_lat],  # Untere linke Ecke
            [mant_lon, muc_lat]  # Zurück zur oberen linken Ecke
        ]
    ]
}

# Bestimmter Zeitraum für die Abfrage (drei Monate)
start_date = "2023-07-01"
end_date = "2023-07-31"
date_range = f"{start_date}/{end_date}"

# Durchsucht die Sentinel-2 Level-2A Sammlung nach Datensätzen, die die angegebenen Kriterien erfüllen
search = client.search(
    collections=[collection], intersects=geometry, datetime=date_range
)

# Gibt die gefundenen Datensätze als GeoJSON-Dictionary aus
print(search.item_collection_as_dict())

# Zusätzliche Filter, z.B. Wolkenbedeckung < 20% und Vegetationsanteil > 25%
filters = {
    "eo:cloud_cover": {"lt": 0.2},
}

# Durchsucht die Sammlung mit den zusätzlichen Filtern
search = client.search(collections=[collection], intersects=geometry, query=filters, datetime=date_range)

# Gibt die gefundenen Datensätze als GeoJSON-Dictionary aus
print(search.item_collection_as_dict())

# Lädt die Daten in xarray-Format
data = load(search.items(), geopolygon=geometry, groupby="solar_day", chunks={})
print(data)

# Umrechnung von nir und red
nir = data.nir.astype(np.float32) / 65535.0
red = data.red.astype(np.float32) / 65535.0

# Berechnet den NDVI
ndvi = (nir - red) / (nir + red)


# Exportiert die Daten als GeoTIFF
output_path = r'C:\Users\jomas\Documents\Uni\Master_Semester_4\pythonaut\Projekt_neu\SRTM\ndvi_test.tif'
odc.geo.xr.write_cog(ndvi, fname=output_path, overwrite=True)
print(f"Die NDVI-Datei wurde unter {output_path} gespeichert.")
