import psycopg2
import psycopg2.extras
import json
import requests
from shapely.geometry import mapping, shape, Point, LineString
from shapely.ops import unary_union
from shapely.validation import make_valid
import pickle
import os

from shapely.geometry.collection import GeometryCollection

def get_hospital_records():
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres port=15432 password=password")

    # Open a cursor to perform database operations
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    osm_query = """select ST_AsText(ST_Transform(ST_Centroid(way),4326)) as centroid,osm_id,name from planet_osm_polygon where amenity='hospital'"""
    cur.execute(osm_query)

    polygon_records = cur.fetchall()

    osm_query = """select ST_AsText(ST_Transform(way,4326)) as centroid,osm_id,name from planet_osm_point where amenity='hospital'"""

    cur.execute(osm_query)

    point_records = cur.fetchall()

    return polygon_records + point_records

def structure_record(record):
    name = record["name"]
    center = record["centroid"]
    lon, lat = center.replace("POINT(", "").replace(")", "").split(" ")
    lon = float(lon)
    lat = float(lat)

    return {"name": name, "lon": lon, "lat": lat, "osm_id": record["osm_id"]}

if os.path.isfile("hospitals.json"):
    with open("hospitals.json", "r") as f:
        all_records = json.load(f)
        structured_records = [structure_record(record) for record in all_records]
else:
    all_records = get_hospital_records()
    structured_records = [structure_record(record) for record in all_records]
    with open("hospitals.json", "w") as f:
        json.dump(all_records, f)

features = []

for item in all_records:
    point = Point(float(item['centroid'].split()[0][6:]), float(item['centroid'].split()[1][:-1]))
    features.append({
        'type': 'Feature',
        'geometry': mapping(point),
        'properties': {
            'osm_id': item['osm_id'],
            'name': item['name']
        }
    })

geojson = {
    'type': 'FeatureCollection',
    'features': features
}

with open('hospitals_layer.json', 'w') as f:
    json.dump(geojson, f)

print('GeoJSON data written to file: hospitals_layer.json')

if os.path.isfile("iso_contours.pickle"):
    with open("iso_contours.pickle", "rb") as f:
        isochrone_contours = pickle.load(f)
else:
    isochrone_contours = [[], [], [], []]

    hospitals = []

    for idx, record in enumerate(structured_records):
        print(f"{idx + 1},  of  {len(structured_records)}")
        name = record["name"]
        lon = record["lon"]
        lat = record["lat"]

        payload = {
            "locations":[
                {"lat": lat,"lon": lon}
            ],
            "costing":"auto",
            "denoise":"0.5",
            "generalize":"0",
            "contours":[{"time":10},{"time":20},{"time":30},{"time":40}],
            "polygons":True
        }

        request = f"http://localhost:8002/isochrone?json={json.dumps(payload)}"
        isochrone = requests.get(request).json()

        for idx, geometry in enumerate(isochrone['features']):
            isochrone_contours[idx].append(geometry['geometry'])

    with open("iso_contours.pickle", "wb") as f:
        pickle.dump(isochrone_contours, f)

for idx, geometries in enumerate(isochrone_contours):
    isochrone_geoms = []

    for geom in geometries:
        geom_shape = shape(geom)
        if not geom_shape.is_valid:
            geom_shapes = make_valid(geom_shape)
            x = make_valid(shape(geom))
            if (type(x) == GeometryCollection):
                for y in x.geoms:
                    if type(y) != LineString:
                        isochrone_geoms.append(y)
            else:
                isochrone_geoms.append(x)
        else:
            isochrone_geoms.append(geom_shape)


    print("Finding union")
    print(len(geometries))
    u = unary_union(isochrone_geoms)

    with open(f"polygon_{idx}.json", "w") as f:
        json.dump(mapping(u), f)
