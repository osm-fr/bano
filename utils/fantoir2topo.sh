#!/bin/bash

psql -d cadastre -U cadastre --csv -f fantoir2topo.sql > fantoir_202304.csv
cat fantoir_202304.csv|psql -d bano -U cadastre -c"TRUNCATE topo;COPY topo FROM STDIN WITH CSV HEADER"
rm fantoir_202304.csv