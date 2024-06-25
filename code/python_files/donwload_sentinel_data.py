# online download von sentinel bändern
# weiß nicht ob das geht, für indien hats funktioniert

from pystac_client import Client
from odc.stac import load
import odc.geo

# use publically available stac link such as
client = Client.open("https://earth-search.aws.element84.com/v1") 

# ID of the collection
collection = "sentinel-2-l2a"

# Geometry of AOI
geometry = {
    "coordinates": [
        [
            [47.323941, 19.46556170905807],
            [74.6629598736763, 19.466339343697722],
            [74.6640371158719, 19.4667885366414],
            [74.66395296156406, 19.46614872872264],
        ]
    ],
    "type": "Polygon",
}

# Complete month
date_YYMM = "2023-01"
# run pystac client search to see available dataset
search = client.search(
    collections=[collection], intersects=geometry, datetime=date_YYMM
) 
# spit out data as GeoJSON dictionary
print(search.item_collection_as_dict())
# loop through each item
for item in search.items_as_dicts():
    print(item)

# additional filters as per metadata 
filters = {
    "eo:cloud_cover":{"lt":0.2},
    "s2:vegetation_percentage": {"gt": 25}
}
# run pystac client search to see available dataset 
search = client.search(collections=[collection], intersects=geometry , query=filters ,datetime=date_YYMM) #bbox=tas_bbox
#spit out data as GeoJSON dictionary
print(search.item_collection_as_dict())
# loop through each item
for item in search.items_as_dicts():
    print(item)

#load the data in xarray format
data = load(search.items() ,geopolygon=geometry,groupby="solar_day", chunks={})
print(data)

# create the index without considering scale or offset
ndvi = (data.nir - data.red) / (data.nir + data.red)

# export data as tiff
odc.geo.xr.write_cog(ndvi,fname='ndvi_india.tiff',  overwrite=True)