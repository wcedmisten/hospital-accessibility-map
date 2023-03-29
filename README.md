# Download OSM extract

https://download.geofabrik.de/north-america/us/virginia.html

# Download Population Grid

https://ghsl.jrc.ec.europa.eu/download.php?ds=pop

Select GHS-POP 2020 100m Mollweide

# Set up

## PostGIS

Start up PostGIS

```
cd osm2pgsql
docker compose up -d
```

### osm2pgsql

Install the osm2pgsql tool:

```
apt install osm2pgsql
```

Import the data. This will take a few minutes or many hours depending on the size and your hardware.

```
# replace /path/to/extract.osm.pbf with the actual file path, e.g. ~/Downloads/virginia-latest.osm.pbf
PGPASSWORD=password osm2pgsql --create --verbose -P 15432 -U postgres -H localhost -S osm2pgsql.style /path/to/extract.osm.pbf
```

## Valhalla

Copy osm extract to `custom_files/`

```
cd ..
mkdir custom_files/
cp /path/to/extract.osm.pbf custom_files/
```

Run valhalla with:

```
docker run -dt -v $PWD/custom_files:/custom_files -p 8002:8002 --name valhalla gisops/valhalla:latest
```

Afterwards run
```
docker logs -f valhalla
```

until you see the line `INFO: Found config file. Starting valhalla service!`

# Find the hospitals and all isochrone data for them

Retrieves isochrones within distance of all hospitals.

```
python3 query_hospitals.py
```

## Convert isochrone polygons to mbtiles

### Install tippecanoe

Follow the instructions here: https://github.com/felt/tippecanoe

Convert the geoJson polygons to mbtiles

```
tippecanoe -f polygon_0.json -f polygon_1.json -f polygon_2.json -f polygon_3.json -o virginia_iso.mbtiles
```

### Install go-pmtiles

https://github.com/protomaps/go-pmtiles

### Convert mbtiles to PMTiles format

```
git clone https://github.com/protomaps/go-pmtiles
cd go-pmtiles/
go run main convert virginia_iso.mbtiles virginia_iso.pmtiles
```

# Generating a base map

```
git clone https://github.com/openmaptiles/openmaptiles
cd openmaptiles
# replace virginia with whatever area you want
# see here for supported regions https://github.com/openmaptiles/openmaptiles/blob/master/QUICKSTART.md
./quickstart.sh virginia
```

Alternatively, you can use a custom extract with:
```
mkdir -p data
mv mydata.osm.pbf data/
make generate-bbox-file area=mydata
./quickstart.sh mydata
```

This will create another `.mbtiles` file under `data/tiles.mbtiles`


# population.py

Examines population data within a polygon.


