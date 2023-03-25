import pprint
import webbrowser
import folium
import psycopg2
import psycopg2.extras
import json
import requests
from shapely.geometry import mapping, shape, Polygon
from shapely.ops import unary_union


conn = psycopg2.connect("host=localhost dbname=postgres user=postgres port=15432 password=password")

# Open a cursor to perform database operations
cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

osm_query = """select ST_AsText(ST_Transform(ST_Centroid(way),4326)) as centroid,osm_id,name from planet_osm_polygon where amenity='hospital'"""

cur.execute(osm_query)

polygon_records = cur.fetchall()

osm_query = """select ST_AsText(ST_Transform(way,4326)) as centroid,osm_id,name from planet_osm_point where amenity='hospital'"""

cur.execute(osm_query)

point_records = cur.fetchall()

print(point_records)

MAX_TRAVEL_TIME = 30
m = folium.Map(location=[36.86498460006988, -76.02608518502626], zoom_start=10, tiles='CartoDB positron')


isochrone_countors = [[], [], [], []]

for idx, record in enumerate(polygon_records):
    print(f"{idx + 1},  of  {len(polygon_records)}")
    name = record["name"]
    center = record["centroid"]
    lon, lat = center.replace("POINT(", "").replace(")", "").split(" ")
    lon = float(lon)
    lat = float(lat)

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

    # geom = json.dumps(isochrone['features'][0]['geometry'])

    for idx, geometry in enumerate(isochrone['features']):
        isochrone_countors[idx].append(geometry['geometry'])

    # geo_j = folium.GeoJson(data=geom, style_function=lambda x: {'fillColor': 'orange'})
    # folium.Popup(name).add_to(geo_j)
    folium.Marker([lat, lon], popup=name).add_to(m)
    # geo_j.add_to(m)

for idx, record in enumerate(point_records):
    print(f"{idx + 1},  of  {len(point_records)}")
    name = record["name"]
    center = record["centroid"]
    lon, lat = center.replace("POINT(", "").replace(")", "").split(" ")
    lon = float(lon)
    lat = float(lat)

    payload = {
        "locations":[
            {"lat": lat,"lon": lon}
        ],
        "costing":"auto",
        "denoise":"1",
        "generalize":"0",
        "contours":[{"time":10},{"time":20},{"time":30},{"time":40}],
        "polygons":True
    }

    request = f"http://localhost:8002/isochrone?json={json.dumps(payload)}"
    isochrone = requests.get(request).json()

    # geom = json.dumps(isochrone['features'][0]['geometry'])

    for idx, geometry in enumerate(isochrone['features']):
        isochrone_countors[idx].append(geometry['geometry'])

    # geo_j = folium.GeoJson(data=geom, style_function=lambda x: {'fillColor': 'orange'})
    # folium.Popup(name).add_to(geo_j)
    folium.Marker([lat, lon], popup=name).add_to(m)
    # geo_j.add_to(m)

colors = ['#a83c32', '#e68040', '#edcd2b', '#74e344']

for idx, geometries in enumerate(isochrone_countors):
    isochrone_geoms = [shape(geom) for geom in geometries]

    print("Finding union")
    print(len(geometries))
    u = unary_union(isochrone_geoms)

    with open(f"polygon_{idx}.json", "w") as f:
        json.dump(mapping(u), f)

    print(colors[idx])

    fillColor = colors[idx]
    color = colors[idx]
    style_function = lambda x, fillColor=fillColor, color=color: {
        "fillColor": fillColor,
        "color": color
    }

    if type(u) is Polygon:
        geom = json.dumps(mapping(u))

        geo_j = folium.GeoJson(data=geom, style_function=style_function)
        folium.Popup(name).add_to(geo_j)
        folium.Marker([lat, lon]).add_to(m)
        geo_j.add_to(m)
    else:
        for union_iso in u.geoms:
            geom = json.dumps(mapping(union_iso))

            geo_j = folium.GeoJson(data=geom, style_function=style_function)
            folium.Popup(name).add_to(geo_j)
            folium.Marker([lat, lon]).add_to(m)
            geo_j.add_to(m)

output_file = "map2.html"
m.save(output_file)
webbrowser.open(output_file, new=2)