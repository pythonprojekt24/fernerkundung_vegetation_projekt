### anderer Versuch Höhe einzulesen. Kommt ganz anderes Ergebnis heraus, das aber auch unlogisch ist

import rasterio
import os
import numpy as np
import math

import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
import matplotlib.pyplot as plt

# Höhenraster 
in_grid = r"data\dgm\SRTM\cropped_resampled_merged_dem_utm.tif"

# Pixel in numpy-array umwandeln
raster_dataset = rasterio.open(in_grid, "r", driver="GTiff")

#metadata
NROWS = raster_dataset.height 
NCOLS = raster_dataset.width 
trans = raster_dataset.transform
ULX = trans[2] # Upper left corner X coordinate
ULY = trans[5] # Upper left corner Y coordinate
Cellsize = trans[0]
crs = raster_dataset.crs

# get array
dem_array = raster_dataset.read(1)


# Funktion zum Erzeugen von Punkten entlang einer Linie
def interpolate_points(line, num_points):
    line_length = line.length
    distances = np.linspace(0, line_length, num_points)
    points = [line.interpolate(distance) for distance in distances]
    return points

# Linienshapefile einlesen
in_shp = r"data\shp\line_muc_mant.shp"
gdf_line = gpd.read_file(in_shp)

# Annahme: Das Shapefile enthält nur eine Linie
line = gdf_line.geometry.iloc[0]

# Anzahl der zu interpolierenden Punkte
num_points = 350000

# Punkte entlang der Linie interpolieren
points = interpolate_points(line, num_points)

# Geopandas GeoDataFrame erstellen
points_gdf = gpd.GeoDataFrame(geometry=points, crs=gdf_line.crs)

# Shapefile speichern
out_shp_points = r"data\shp\line_muc_mant_points.shp"
points_gdf.to_file(out_shp_points)

print(f"Erfolgreich {num_points} Punkte entlang der Linie interpoliert und als Shapefile gespeichert.")


# Linienshapefile einlesen
in_shp_points = r"data\shp\line_muc_mant_points.shp"
gdf = gpd.read_file(in_shp_points)
crs = gdf.crs
data_track = gdf.columns.tolist()

# get attribute table structure of input into dictionary
attribute_columns = {}
field_count = len(data_track) - 1
for i in range(field_count):
    field_name = data_track[i]
    attribute_columns[field_name] = []

# add additional attributes
attribute_columns["Height"] = []
attribute_columns["Distance"] = []

# get entries (attributes and geometry)
geom_out = []
TotalDistance = 0

for index, row in gdf.iterrows(): # for each feature of the shapefile
    
    if type(row.geometry) == Point:

        ## copy attributes of input
        for i in range(field_count):
            field_name = data_track[i]
            value = row[data_track[i]]
            attribute_columns[field_name].append(value)

        coords = [row.geometry.x, row.geometry.y]
        geom_out.append(Point(coords))

        # get grid coordinates for point
        gx, gy = rasterio.transform.rowcol(trans, row.geometry.x, row.geometry.y)

        # Debugging: Koordinaten überprüfen
        print(f"Point: ({row.geometry.x}, {row.geometry.y}), Raster coords: ({gx}, {gy})")

        if 0 <= gx < NCOLS and 0 <= gy < NROWS:
            Height = dem_array[gy, gx]
        else:
            Height = np.nan
            print(f"Warning: Point ({row.geometry.x}, {row.geometry.y}) is out of raster bounds.")

        # fill additional attribute
        attribute_columns["Height"].append(Height)

        if index == 0:
            attribute_columns["Distance"].append(0.0)
        else:
            Dist = math.sqrt((geom_out[-2].x-geom_out[-1].x)**2+(geom_out[-2].y-geom_out[-1].y)**2)
            TotalDistance += Dist
            attribute_columns["Distance"].append(TotalDistance)

##
# Debugging-Ausgabe: Überprüfen Sie die Längen der Listen in attribute_columns
for key, value in attribute_columns.items():
    print(f"Length of {key}: {len(value)}")
print(f"Length of geom_out: {len(geom_out)}")

# Überprüfen Sie, ob alle Listen die gleiche Länge haben
list_lengths = [len(v) for v in attribute_columns.values()]
if len(set(list_lengths)) != 1:
    print("Fehler: Nicht alle Listen in attribute_columns haben die gleiche Länge.")
    # Optional: Zusätzliche Debugging-Ausgaben
    for key, value in attribute_columns.items():
        print(f"{key}: {value}")

# Geopandas ist funktion zum lesen/verwenden von shapefiles
out_shp = r"data\shp\track_muc_mant_elevation.shp"
if len(set(list_lengths)) == 1:
    points_out = gpd.GeoDataFrame(
        data=attribute_columns,
        geometry=geom_out,
        crs=crs
    )
    points_out.to_file(out_shp)

    # Höhenprofil plotten
    plt.plot(attribute_columns["Distance"], attribute_columns["Height"], "r-")

    # title, axis labels etc.
    plt.title("Höhenlage pro Strecke von München nach Mantova", fontsize=12)
    plt.ylabel("Höhe [m]")
    plt.xlabel("Strecke [m]")

    plt.savefig(r"plots\elevation_distance_plot.png", dpi=300)
    plt.show()
else:
    print("Fehler: Die GeoDataFrame wurde nicht erstellt, da die Listenlängen nicht übereinstimmen.")
