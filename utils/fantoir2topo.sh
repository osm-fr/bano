#!/bin/bash

set -e

$pgsql_CADASTRE --csv -f fantoir2topo.sql > fantoir_202304.csv
$pgsql_BANO -v ON_ERROR_STOP=1 -c "TRUNCATE topo; COPY topo FROM STDIN WITH CSV HEADER"
rm fantoir_202304.csv
