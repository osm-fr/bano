#!/bin/bash

set -e

source config

set -e

cd $TMP_DIR
pg_dump -t ${1} "postgresql://${PGCON_OSM}" > ${1}_dump.sql
$pgsql_CADASTRE -c "DROP TABLE IF EXISTS ${1} CASCADE;"
$pgsql_CADASTRE -f ${1}_dump.sql
rm -f ${1}_dump.sql
