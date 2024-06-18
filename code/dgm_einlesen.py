import rasterio
import os
import numpy as np
import math

import geopandas as gpd
from shapely.geometry import Point,LineString,Polygon,MultiPolygon
import matplotlib.pyplot as plt

# Höhenraster 
in_grid = r"data\dgm\DGM_EU.tif" # müssen wir dann so nennen und vermutlich auf keinen Fall committen, sondern nur lokal ausführen!

# Pixel in numpy-array umwandeln
# dataset
raster_dataset = rasterio.open(in_grid, "r", driver="GTiff")

#metadata --> machen Bild zu georeferenziertem Datensatz
NROWS = raster_dataset.height 
NCOLS = raster_dataset.width 
trans = raster_dataset.transform # links oben und Mitte Auflösung, rechts: Koordinaten
ULX = trans[2] #ul: upper left corner --> sagt in Echtwelt-koordinaten, wo bild aufgehängt ist (x)
ULY = trans[5] 
Cellsize = trans[0] # daraus und aus Eckkoord. können wir genauen Pkt. berechnen
crs = raster_dataset.crs # epsg-code

# get array
dem_array = raster_dataset.read(1) # extract as numpy array # 1 für 1. Band
#print(dem_array)
#print(dem_array[0,0])
#print(ULX, ULY) # gibt uns in UTM die linken Eckkoordin. aus

##########################################################
# Shapefile einlesen
in_shp = r"data\shp\line.shp" # passend benennen!
gdf = gpd.GeoDataFrame.from_file(in_shp)

crs = gdf.crs
data_track = gdf.columns.tolist()

# get attribute table structure of input into dictionary
attribute_columns = {}
field_count = len(data_track)-1
for i in range(field_count):
    field_name = data_track[i]
    attribute_columns[field_name] =[]
#print(attribute_columns)

# add additional attributes
attribute_columns["Height"] =[]
attribute_columns["Distance"]=[]

# get entries (attributes and geometry)
geom_out = []

TotalDistance = 0
for index, row in gdf.iterrows():   
    ## copy attributes of input
    for i in range(field_count):
        field_name = data_track[i]
        value = row[data_track[i]]
        attribute_columns[field_name].append(value)
    if type(row.geometry) == Point:
        coords = [row.geometry.x, row.geometry.y]
        geom_out.append(Point(coords)) 

     # get grid coordinates for point
        gx = int((row.geometry.x-ULX)/Cellsize) # entfernung von linker ecke/cellsize
        gy = int((row.geometry.y-ULY)/-Cellsize)
        if gx > NCOLS and gx < 0:
            continue
        if gy > NROWS and gy < 0:
            continue
        Height = dem_array[gy,gx]

        # fill additional attribute
        attribute_columns["Height"].append(Height)

        if(index == 0):
            attribute_columns["Distance"].append(0.0)
        else:
            Dist = math.sqrt((geom_out[-2].x-geom_out[-1].x)**2+(geom_out[-2].y-geom_out[-1].y)**2) 
            TotalDistance+=Dist 
            attribute_columns["Distance"].append(TotalDistance)


# geopandas ist funktion zum lesen/verwenden von shapefiles

out_shp = r"data\shp\track_elevation.shp"
##create new output
points_out = gpd.GeoDataFrame(
    data=attribute_columns,
    geometry = geom_out,
    crs=crs
)
points_out.to_file(out_shp)


# Höhenprofil plotten
plt.plot(attribute_columns["Distance"], attribute_columns["Height"],"r-")

# title, axis labels etc.
plt.title("Höhenlage pro Strecke", fontsize=12)
plt.ylabel("Höhe [m]")
plt.xlabel("Strecke [m]")

plt.savefig(r"..\plots\elevation_distance_plot.png", dpi=300)
plt.show()


