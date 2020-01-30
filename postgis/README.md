# database_setup

This makes a database with the required plant, climate, and biome data to build the plant finder app. The plant data and one piece of the biome data cannot be acquired automatically so in addition to installing the relevant programs one must also acquire these additional data.
Plant data: location data from https://fallingfruit.org/data
Plant data: location data from https://www.gbif.org/occurrence/search?country=US&has_coordinate=true&has_geospatial_issue=false&taxon_key=6
biome data: additional land data from https://www.usgs.gov/core-science-systems/science-analytics-and-synthesis/gap/science/land-cover-data-download?qt-science_center_objects=0#qt-science_center_objects

## Software Requirements

Requires:
    - make
    - python3
    - docker
    - curl
    - unzip
    - raster2pgsql (installed via `brew install postgis`)
    - shp2pgsql (installed via `brew install postgis`)
