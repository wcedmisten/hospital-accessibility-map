import json
from shapely.geometry import Point, mapping

with open('hospitals.json') as f:
    data = json.load(f)

features = []

for item in data:
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