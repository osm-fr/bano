#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

set -e

cd $TMP_DIR
pg_dump -t ${1} "postgresql://${PGCON_OSM}" > ${1}_dump.sql
$pgsql_CADASTRE -c "DROP TABLE IF EXISTS ${1} CASCADE;"
$pgsql_CADASTRE -f ${1}_dump.sql
rm -f ${1}_dump.sql
