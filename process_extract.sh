# set -euxo pipefail

OSM_PBF_DIRECTORY=/home/wcedmisten/Downloads
OSM_PBF_FILENAME=virginia-latest.osm.pbf
OSM_PBF="$OSM_PBF_DIRECTORY/$OSM_PBF_FILENAME"

echo "Processing extract at $OSM_PBF"

cd osm2pgsql
echo "Starting PostGIS"
docker compose up -d

sleep 10

PGPASSWORD=password osm2pgsql --create --verbose -P 15432 -U postgres -H localhost -S osm2pgsql.style $OSM_PBF
cd ..


cp $OSM_PBF planetiler_data
docker run -e JAVA_TOOL_OPTIONS="-Xmx4g" -v "$(pwd)/planetiler_data":/data ghcr.io/onthegomap/planetiler:latest --download --osm-path=/data/$OSM_PBF_FILENAME --output /data/basemap.pmtiles --maxzoom=8

cp $OSM_PBF valhalla_data
docker run -dt -v $PWD/valhalla_data:/custom_files -p 8002:8002 --name valhalla gisops/valhalla:3.3.0

echo "Waiting for valhalla to finish import"
until $(curl --output /dev/null --silent --fail localhost:8002/status); do
    printf '.'
    sleep 30
done

echo "Valhalla import finished"

echo "Imports completed. Running Python script to find driving distance polygons."

python3 query_hospitals.py

echo "Converting polygons into tiles"

tippecanoe --simplification 6 -f polygon_0.json -f polygon_1.json -f polygon_2.json -f polygon_3.json -o ${OSM_PBF_FILENAME}_iso.mbtiles

cd go-pmtiles/
go install
go run main.go convert ../${OSM_PBF_FILENAME}_iso.mbtiles ../${OSM_PBF_FILENAME}_iso.pmtiles
cd ..

echo "Output completed. Final files:"
echo "planetiler_data/basemap.pmtiles"
echo "hospitals_layer.json"
echo "$OSM_PBF_FILENAME_iso.pmtiles"
