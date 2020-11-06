#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

set -e

cd $TMP_DIR
pg_dump -t ${1} -U cadastre osm > ${1}_dump.sql
psql -d cadastre -U cadastre -c "DROP TABLE IF EXISTS ${1} CASCADE;"
psql -d cadastre -U cadastre -f ${1}_dump.sql
rm -f ${1}_dump.sql
