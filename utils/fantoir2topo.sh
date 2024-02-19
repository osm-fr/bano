#!/bin/bash

$pgsql_CADASTRE --csv -f fantoir2topo.sql > fantoir_202304.csv
cat fantoir_202304.csv| $pgsql_BANO -c "TRUNCATE topo; COPY topo FROM STDIN WITH CSV HEADER"
rm fantoir_202304.csv
