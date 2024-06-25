import geopandas as gpd
from shapely.geometry import LineString
import gpxpy
import gpxpy.gpx

# Koordinaten für München und Verona (WGS84)
munich_coords = (11.5820, 48.1351)  # Längengrad, Breitengrad
verona_coords = (10.9916, 45.4384)  # Längengrad, Breitengrad

# Erstelle eine Linie von München nach Verona
line = LineString([munich_coords, verona_coords])

# Erstelle ein GeoDataFrame
gdf = gpd.GeoDataFrame([{'geometry': line}], crs="EPSG:4326")

# Speichere das GeoDataFrame als Shapefile
shapefile_path = "munich_verona_line.shp"
gdf.to_file(shapefile_path, driver='ESRI Shapefile')

print(f"Shapefile erfolgreich erstellt: {shapefile_path}")

# Lese das Shapefile erneut ein, um die Geometrie zu extrahieren
gdf = gpd.read_file(shapefile_path)

# Erstelle ein GPX-Objekt
gpx = gpxpy.gpx.GPX()

# Erstelle einen GPX-Track
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Erstelle einen GPX-Track-Segment
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# Iteriere über die Geometrien im GeoDataFrame und füge sie als GPX-Punkte hinzu
for geom in gdf.geometry:
    if geom.type == 'LineString':
        for coord in geom.coords:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[1], coord[0]))

# Speichere die GPX-Datei
gpx_file_path = "munich_verona_line.gpx"
with open(gpx_file_path, 'w') as f:
    f.write(gpx.to_xml())

print(f"GPX-Datei erfolgreich erstellt: {gpx_file_path}")

