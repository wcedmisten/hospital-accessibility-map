# Download OSM extract

https://download.geofabrik.de/north-america/us/virginia.html

# Download Population Grid

https://ghsl.jrc.ec.europa.eu/download.php?ds=pop

Select GHS-POP 2020 100m Mollweide

# Set up

Install https://github.com/wcedmisten/osm2pgsql-docker using OSM extract

Copy osm extract to `custom_files/`

Run valhalla with:

```
docker run -dt -v $PWD/custom_files:/custom_files -p 8002:8002 --name valhalla gisops/valhalla:latest
```

# population.py

Examines population data within a polygon.

# query_hospitals.py

Retrieves isochrones within distance of all hospitals.
