import json
import rasterio

import rasterio
from rasterio.features import geometry_window

from shapely.geometry import shape
from shapely.ops import unary_union

import rasterio
from rasterstats import zonal_stats

from shapely.ops import transform
import pyproj

GHS_POP_FILENAME = (
    "/home/wcedmisten/Downloads/GHS_POP_E2020_GLOBE_R2022A_54009_100_V1_0.tif"
)

dc_geom = """{
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -83.59040921031028,
              36.64493325346298
            ],
            [
              -75.86288564384472,
              36.54557820497291
            ],
            [
              -75.26475881974928,
              38.0169901518764
            ],
            [
              -76.15163652444231,
              37.89230860939507
            ],
            [
              -77.07288933396738,
              38.90522302216186
            ],
            [
              -78.26914298215678,
              39.59201849940126
            ],
            [
              -83.59040921031028,
              36.64493325346298
            ]
          ]
        ],
        "type": "Polygon"
      } }"""

dataset = rasterio.open(
    GHS_POP_FILENAME
)  # Note GetRasterBand() takes band no. starting from 1 not 0

for i in range(4):
  with open(f"polygon_{i}.json", "r") as f:
      geom = json.load(f)

  # print(geom["geometry"]["coordinates"])
  polygon = shape(geom)

  project = pyproj.Transformer.from_proj(
          pyproj.Proj('epsg:4326'), # source coordinate system
          pyproj.Proj('esri:54009'),
          always_xy=True
  )

  projected = transform(project.transform, polygon)

  window = geometry_window(dataset, [projected] ,pad_x=10, pad_y=10)

  z = dataset.read(masked=True, window=window)[0]
  print(dataset.crs)
  print(dataset.bounds)
  print({i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)})

  zs = zonal_stats(projected, GHS_POP_FILENAME, stats="sum")
  near_hospitals = zs[0]["sum"]
  print(near_hospitals)

  with open("states.json", "r") as f:
      states = json.load(f)

  virginia = states["features"][46]
  va_geom = shape(virginia["geometry"])

  va_projected = transform(project.transform, va_geom)

  va_union_projected = unary_union([va_projected, projected])

  window = geometry_window(dataset, [va_union_projected] ,pad_x=10, pad_y=10)

  z = dataset.read(masked=True, window=window)[0]
  print(dataset.crs)
  print(dataset.bounds)
  print({i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)})

  zs = zonal_stats(va_union_projected, GHS_POP_FILENAME, stats="sum")
  in_va = zs[0]["sum"]
  print(in_va)

  print(f"{near_hospitals} / {in_va}")
  print(near_hospitals / in_va)

# src = rasterio.open(FILENAME)
# from rasterio.plot import show

# show(src, cmap="viridis", vmin=0, vmax=300)
