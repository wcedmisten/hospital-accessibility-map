import json
import numpy as np
import rasterio
from rasterio.warp import reproject
from rasterio.enums import Resampling

import rasterio
from pyproj.crs import CRS
from pyproj.enums import WktVersion
from rasterio.windows import Window

from shapely.geometry import Polygon, mapping, shape

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterstats import zonal_stats

# FILENAME = '/home/wcedmisten/Downloads/GHS_POP_E2020_GLOBE_R2022A_54009_100_V1_0_R5_C12.tif'
FILENAME = (
    "/home/wcedmisten/Downloads/GHS_POP_E2020_GLOBE_R2022A_54009_100_V1_0_R5_C12.tif"
)
NEW_FILENAME = "/tmp/RGB.byte.wgs84.tif"

dst_crs = "EPSG:4326"

# with rasterio.open(FILENAME) as src:
#     transform, width, height = calculate_default_transform(
#         src.crs, dst_crs, src.width, src.height, *src.bounds)
#     kwargs = src.meta.copy()
#     kwargs.update({
#         'crs': dst_crs,
#         'transform': transform,
#         'width': width,
#         'height': height
#     })

#     with rasterio.open(NEW_FILENAME, 'w', **kwargs) as dst:
#         for i in range(1, src.count + 1):
#             reproject(
#                 source=rasterio.band(src, i),
#                 destination=rasterio.band(dst, i),
#                 src_transform=src.transform,
#                 src_crs=src.crs,
#                 dst_transform=transform,
#                 dst_crs=dst_crs,
#                 resampling=Resampling.average)

geom = """{
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              -77.04117721046109,
              38.995600398548305
            ],
            [
              -77.11917446437272,
              38.934955418936426
            ],
            [
              -77.10007970096741,
              38.9125464306525
            ],
            [
              -77.08422133813832,
              38.90473939074829
            ],
            [
              -77.06642113496387,
              38.90096148255358
            ],
            [
              -77.029526168383,
              38.863675346207884
            ],
            [
              -77.0262897678056,
              38.8019086780142
            ],
            [
              -76.91010298708221,
              38.89315316861794
            ],
            [
              -77.04117721046109,
              38.995600398548305
            ]
          ]
        ],
        "type": "Polygon"
      }
    }"""

poly_arr = [
    [-77.04139451602279, 38.995501118547594],
    [-77.11994205319124, 38.93501362389631],
    [-77.0396378618371, 38.791980219139646],
    [-76.90964545208261, 38.892836974204045],
    [-77.04139451602279, 38.995501118547594],
]

from shapely.ops import transform
import pyproj
from functools import partial

print(json.loads(geom)["geometry"]["coordinates"])
polygon = Polygon(json.loads(geom)["geometry"]["coordinates"][0])

project = pyproj.Transformer.from_proj(
        pyproj.Proj('epsg:4326'), # source coordinate system
        pyproj.Proj('esri:54009'),
        always_xy=True
)

projected = transform(project.transform, polygon)

print(polygon)
print(projected)

dataset = rasterio.open(
    FILENAME
)  # Note GetRasterBand() takes band no. starting from 1 not 0

z = dataset.read(masked=True)[0]
print(dataset.crs)
print(dataset.bounds)
print({i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)})

zs = zonal_stats(projected, FILENAME, stats="min max median mean sum")
print(zs)

src = rasterio.open(FILENAME)
from rasterio.plot import show

show(src, cmap="viridis", vmin=0, vmax=300)

src = rasterio.open(NEW_FILENAME)
from rasterio.plot import show

show(src, cmap="viridis", vmin=0, vmax=300)