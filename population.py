import json
import rasterio

import rasterio
from rasterio.features import geometry_window

from shapely.geometry import shape, mapping
from shapely.ops import unary_union

import rasterio
from rasterstats import zonal_stats

from shapely.ops import transform
import pyproj
from pyproj import Geod

GHS_POP_FILENAME = (
    "/home/wcedmisten/Downloads/GHS_POP_E2020_GLOBE_R2022A_54009_100_V1_0.tif"
)

# GHS_POP_FILENAME = "/home/wcedmisten/Downloads/GHS_POP_E2020_GLOBE_R2022A_54009_100_V1_0_R5_C11.tif"

# src = rasterio.open(GHS_POP_FILENAME)
# from rasterio.plot import show

# show(src, cmap="viridis", vmin=0, vmax=60)

# this was a sanity check to see if the DC population lines up with my methods 
# of calculating population within a polygon

dataset = rasterio.open(
    GHS_POP_FILENAME
)  # Note GetRasterBand() takes band no. starting from 1 not 0

project_to_mollweide = pyproj.Transformer.from_proj(
        pyproj.Proj('epsg:4326'), # source coordinate system
        pyproj.Proj('esri:54009'),
        always_xy=True
)

def estimate_population(dataset, geom):
  polygon = shape(geom)

  projected = transform(project_to_mollweide.transform, polygon)

  window = geometry_window(dataset, [projected], pad_x=10, pad_y=10)

  dataset.read(masked=True, window=window)[0]

  zs = zonal_stats(projected, GHS_POP_FILENAME, stats="sum")
  return round(zs[0]["sum"])
  
# sanity check
# with open("dc.json", "r") as f:
#    dc_geom = json.load(f)

# print(estimate_population(dataset, dc_geom))

with open("states.json", "r") as f:
    states = json.load(f)

virginia = states["features"][46]
va_geom = shape(virginia["geometry"])
in_va = estimate_population(dataset, va_geom)

print(f"Estimated population of Virginia: {in_va}")

geod = Geod(ellps="WGS84")
va_area = abs(geod.geometry_area_perimeter(va_geom)[0])

print(f"Area of Virginia: {va_area}")

times = [40, 30, 20, 10]

for i in range(4):
  with open(f"polygon_{i}.json", "r") as f:
      iso_geom = shape(json.load(f))

  # intersection is needed to cut off isochrones that extend beyond VA borders
  # this is because the OSM extract includes roads that don't
  # get cut strictly at the border, but extend into other states
  # we don't want to include those populations in the numerator
  iso_va_intersection = va_geom.intersection(iso_geom)

  near_hospitals = estimate_population(dataset, iso_va_intersection)

  near_hospitals_area = abs(geod.geometry_area_perimeter(iso_va_intersection)[0])

  print(f"Estimated {near_hospitals} residents within {times[i]} mins of a hospital.")
  print(f"{near_hospitals / in_va * 100} percent of Virginia residents")
  print(f"Area of this region: {near_hospitals_area}")
  print(f"{near_hospitals_area / va_area * 100} percent of Virginia surface area")
  print()
