# plant finder

This is a minimal working version of the plant finder app.
It is a docker-compose setup running a postgresql server with postgis extensions and a flask front and back end.

## requirements

- docker-compose
- a google maps api key

## starting up

Put the api key into a `.env` file as `GOOGLE_MAPS_API_KEY=<KEY>` so docker-compose properly passes it onto the flask app.
In addition define a `PG_USER=<user>` and `PG_PASSWORD=<user>` so flask knows how to access the database.
While these could be hard-coded in later versions, the current docker-compose config exposes the postgresql server for testing making it a security risk to deploy this to the web without a firewall.

Initial load times are slow as the models are built from scratch, however, they are pickled for faster load times later.


## data

### Sources

Plant data are from:

- https://fallingfruit.org/data
- https://www.gbif.org/occurrence/search?country=US&has_coordinate=true&has_geospatial_issue=false&taxon_key=6

biome data from:

- https://www.usgs.gov/core-science-systems/science-analytics-and-synthesis/gap/science/land-cover-data-download?qt-science_center_objects=0#qt-science_center_objects

Climate and land data are from:

- ftp://prism.nacse.org/normals_800m/tmax/PRISM_tmax_30yr_normal_800mM2_annual_bil.zip
- ftp://prism.nacse.org/normals_800m/tmin/PRISM_tmin_30yr_normal_800mM2_annual_bil.zip
- ftp://prism.nacse.org/normals_800m/ppt/PRISM_ppt_30yr_normal_800mM2_annual_bil.zip
- http://prism.nacse.org/projects/public/phm/phm_us_grid.zip
- https://s3-us-west-2.amazonaws.com/mrlc/NLCD_2016_Land_Cover_L48_20190424.zip

Massachusetts park data is from:

- http://download.massgis.digital.mass.gov/shapefiles/state/openspace.zip

The postgresql server starts up with already cleaned data.
Earlier attempts to make this had the database build from the raw data but this leads to incredibly long build times as some of the raw data takes quite a while to load into postgresql followed by a long series of sql queries to gather it into the final tables.
Automating it is also difficult as the gbif plant data and the biome data cannot be programmatically downloaded (gbif requires authenticating and the biome data has a captcha).
Documenting/layout the full data pipeline is a TODO but low priority.
