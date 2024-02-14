#!/bin/bash

set -e

psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 --csv -f fantoir2topo.sql > fantoir_202304.csv
cat fantoir_202304.csv| psql -d bano -U cadastre -v ON_ERROR_STOP=1 -c "TRUNCATE topo; COPY topo FROM STDIN WITH CSV HEADER"
rm fantoir_202304.csv
