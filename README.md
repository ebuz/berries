# Huckleberry hunter

This is a deployable version of the Huckleberry hunter app.
It is a docker-compose setup running a PostgreSQL server with [PostGIS](https://postgis.net/) extensions and a flask front/back end.

## requirements

- docker-compose (tested on 1.25.3; may work with as early as 1.22.0)
- a google maps api key [get one here](https://developers.google.com/maps/documentation/javascript/get-api-key)

## starting up

Put the api key into a `.env` file as `GOOGLE_MAPS_API_KEY=<KEY>` so docker-compose properly passes it onto the flask app.
In addition define a `PG_USER=<user>` and `PG_PASSWORD=<user>` so flask knows how to access the database.

### example `.env`

```bash
GOOGLE_MAPS_API_KEY=yourkey
PG_USER=huckleberry
PG_PASSWORD=hunter
```

These can be hard-coded within the `docker-compose.yaml`; however, the current docker-compose configuration exposes the postgresql server making it a security risk to deploy this to the web without a firewall.

Initial start-up takes a while as the predictive models are built from scratch. During this time the web server will not respond to requests. The models are pickled for faster load times on subsequent server restarts so long as the containers are set to persist after shutdown.


## data

### Sources

Plant data are from:

- https://fallingfruit.org/data
- https://www.gbif.org/occurrence/search?country=US&has_coordinate=true&has_geospatial_issue=false&taxon_key=6

Climate and land data are from:

- ftp://prism.nacse.org/normals_800m/tmax/PRISM_tmax_30yr_normal_800mM2_annual_bil.zip
- ftp://prism.nacse.org/normals_800m/tmin/PRISM_tmin_30yr_normal_800mM2_annual_bil.zip
- ftp://prism.nacse.org/normals_800m/ppt/PRISM_ppt_30yr_normal_800mM2_annual_bil.zip
- http://prism.nacse.org/projects/public/phm/phm_us_grid.zip
- https://s3-us-west-2.amazonaws.com/mrlc/NLCD_2016_Land_Cover_L48_20190424.zip

Massachusetts park data is from:

- http://download.massgis.digital.mass.gov/shapefiles/state/openspace.zip

The postgresql server starts up with substantially cleaned data that combines the above sources into a few tables.
Earlier attempts to make this deployable version had the database build from the raw data but this leads to incredibly long build times given the multiple stages needed to join the tabular, raster, and GIS data.
Automating it is also difficult as the gbif plant data and the biome data cannot be programmatically downloaded (gbif requires authenticating and the biome data has a captcha).
Providing a reproducible data pipeline is a TODO but low priority at this time.

## TODO

App load times are quite long, especially if the app is building the models to begin with. It may be better to spin off the model building into a separate stage before the web-server is loaded up. One can also reduce the number of sql calls that involve pulling in GIS data as that is a substantial slowdown in addition to the model building.
