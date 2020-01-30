FROM kartoza/postgis:12.0

ENV POSTGRES_DB=plants
ENV POSTGRES_MULTIPLE_EXTENSIONS=postgis,postgis_raster,hstore,postgis_topology
VOLUME /var/lib/postgresql
ADD ./setup_scripts /docker-entrypoint-initdb.d
