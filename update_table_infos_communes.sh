#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f ./sql/update_table_infos_communes.sql
